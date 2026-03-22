const TRIAL_REGISTRY_KEY = "nutria-pro:trial_registry";
const TRIAL_CURRENT_EMAIL_KEY = "nutria-pro:trial_current_email";
const TRIAL_LEAD_KEY = "nutria-pro:trial_lead";
const TRIAL_DURATION_DAYS = 14;

export type TrialStatus = "lead" | "active" | "expired" | "converted";

export interface TrialRecord {
  email: string;
  status: TrialStatus;
  startedAt: string | null;
  endsAt: string | null;
  createdFromClickAt: string;
  updatedAt: string;
}

function normalizeEmail(email: string): string {
  return email.trim().toLowerCase();
}

function nowIso(): string {
  return new Date().toISOString();
}

function plusDays(date: Date, days: number): Date {
  const copy = new Date(date.getTime());
  copy.setDate(copy.getDate() + days);
  return copy;
}

function readRegistry(): Record<string, TrialRecord> {
  if (typeof window === "undefined") return {};
  const raw = localStorage.getItem(TRIAL_REGISTRY_KEY);
  if (!raw) return {};
  try {
    return JSON.parse(raw) as Record<string, TrialRecord>;
  } catch {
    return {};
  }
}

function writeRegistry(registry: Record<string, TrialRecord>): void {
  if (typeof window === "undefined") return;
  localStorage.setItem(TRIAL_REGISTRY_KEY, JSON.stringify(registry));
}

function recalculateStatus(record: TrialRecord): TrialRecord {
  if (record.status !== "active" || !record.endsAt) return record;
  if (new Date(record.endsAt).getTime() <= Date.now()) {
    return { ...record, status: "expired", updatedAt: nowIso() };
  }
  return record;
}

export function registerTrialLeadFromClick(): void {
  if (typeof window === "undefined") return;
  const lead = { clickedAt: nowIso() };
  localStorage.setItem(TRIAL_LEAD_KEY, JSON.stringify(lead));
}

export function getTrialLeadClickedAt(): string | null {
  if (typeof window === "undefined") return null;
  const raw = localStorage.getItem(TRIAL_LEAD_KEY);
  if (!raw) return null;
  try {
    const parsed = JSON.parse(raw) as { clickedAt?: string };
    return parsed.clickedAt ?? null;
  } catch {
    return null;
  }
}

export function activateTrialForEmail(email: string): TrialRecord {
  const key = normalizeEmail(email);
  const registry = readRegistry();
  const existing = registry[key];
  const start = new Date();
  const end = plusDays(start, TRIAL_DURATION_DAYS);

  const updated: TrialRecord = {
    email: key,
    status: "active",
    startedAt: start.toISOString(),
    endsAt: end.toISOString(),
    createdFromClickAt: existing?.createdFromClickAt ?? getTrialLeadClickedAt() ?? nowIso(),
    updatedAt: nowIso(),
  };

  registry[key] = updated;
  writeRegistry(registry);
  setCurrentTrialEmail(key);
  return updated;
}

export function setCurrentTrialEmail(email: string): void {
  if (typeof window === "undefined") return;
  localStorage.setItem(TRIAL_CURRENT_EMAIL_KEY, normalizeEmail(email));
}

export function getCurrentTrialEmail(): string | null {
  if (typeof window === "undefined") return null;
  return localStorage.getItem(TRIAL_CURRENT_EMAIL_KEY);
}

export function getTrialByEmail(email: string): TrialRecord | null {
  const key = normalizeEmail(email);
  const registry = readRegistry();
  const record = registry[key];
  if (!record) return null;
  const recalculated = recalculateStatus(record);
  if (recalculated.status !== record.status) {
    registry[key] = recalculated;
    writeRegistry(registry);
  }
  return recalculated;
}

export function getCurrentTrial(): TrialRecord | null {
  const email = getCurrentTrialEmail();
  if (!email) return null;
  return getTrialByEmail(email);
}

export function getTrialDaysLeft(record: TrialRecord): number {
  if (!record.endsAt || record.status !== "active") return 0;
  const diff = new Date(record.endsAt).getTime() - Date.now();
  return Math.max(0, Math.ceil(diff / (1000 * 60 * 60 * 24)));
}

export function isTrialExpired(record: TrialRecord | null): boolean {
  if (!record) return false;
  return recalculateStatus(record).status === "expired";
}
