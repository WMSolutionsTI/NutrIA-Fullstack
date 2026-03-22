"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

const links = [
  { href: "/nutricionista/painel", label: "Painel" },
  { href: "/nutricionista/onboarding", label: "Setup Secretária" },
  { href: "/nutricionista/clientes", label: "Clientes" },
  { href: "/nutricionista/agenda", label: "Agenda" },
  { href: "/nutricionista/caixa-de-entrada", label: "Caixa de Entrada" },
  { href: "/nutricionista/mensagens", label: "Mensagens" },
  { href: "/nutricionista/campanhas", label: "Campanhas" },
  { href: "/nutricionista/cobrancas", label: "Cobranças" },
  { href: "/nutricionista/relatorios", label: "Relatórios" },
  { href: "/nutricionista/relatorios-metricas", label: "Métricas" },
  { href: "/nutricionista/plano-alimentar", label: "Plano Alimentar" },
  { href: "/nutricionista/prontuario", label: "Prontuário" },
  { href: "/nutricionista/exames-resultados", label: "Exames" },
  { href: "/nutricionista/configuracoes", label: "Configurações" },
];

export default function NutriSidebar() {
  const pathname = usePathname();

  return (
    <aside className="hidden xl:flex flex-col w-72 min-h-screen border-r border-emerald-100 bg-white/85 backdrop-blur-xl p-6">
      <div className="mb-6 flex items-center gap-3">
        <img src="/globe.svg" alt="NutrIA Pro" className="h-11 w-11 rounded-xl bg-emerald-100 p-2" />
        <div>
          <p className="text-lg font-black text-zinc-900">NutrIA Pro</p>
          <p className="text-xs text-zinc-500">Assistente clínica + comercial</p>
        </div>
      </div>

      <nav className="space-y-1 overflow-y-auto pr-1">
        {links.map((link) => {
          const active = pathname === link.href;
          return (
            <Link
              key={link.href}
              href={link.href}
              className={`block rounded-xl px-4 py-2.5 text-sm font-semibold transition-all ${
                active
                  ? "bg-emerald-500 text-white shadow-[0_8px_24px_rgba(16,185,129,0.35)]"
                  : "text-zinc-700 hover:bg-emerald-50"
              }`}
            >
              {link.label}
            </Link>
          );
        })}
      </nav>

      <div className="mt-auto rounded-2xl border border-emerald-200 bg-gradient-to-br from-emerald-50 to-cyan-50 p-4">
        <p className="text-xs font-bold text-emerald-800">Operação premium</p>
        <p className="mt-1 text-xs text-emerald-700">
          Atendimento, cobrança, agenda e IA unificados em tempo real.
        </p>
      </div>
    </aside>
  );
}
