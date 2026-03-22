"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import React, { useState } from "react";

import { login } from "@/lib/api/auth";
import { getTrialByEmail, isTrialExpired, setCurrentTrialEmail } from "@/lib/trial";

export default function NutriLogin() {
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!email || !password) {
      setError("Preencha todos os campos.");
      return;
    }

    try {
      setLoading(true);
      setError("");
      const user = await login({ email, password });
      setCurrentTrialEmail(email);

      const trial = getTrialByEmail(email);
      if (trial && isTrialExpired(trial)) {
        router.push("/nutricionista/cobrancas?trial=expired");
        router.refresh();
        return;
      }

      if (user.must_change_password) {
        router.push("/nutricionista/primeiro-acesso");
        router.refresh();
        return;
      }

      if (!user.profile_completed) {
        router.push("/nutricionista/completar-cadastro");
        router.refresh();
        return;
      }

      if (!user.setup_completed) {
        router.push("/nutricionista/painel?setup=pendente");
        router.refresh();
        return;
      }

      router.push("/nutricionista/painel");
      router.refresh();
    } catch (err) {
      const message =
        err instanceof Error ? err.message : "Não foi possível autenticar.";
      setError(message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="min-h-screen bg-[radial-gradient(circle_at_10%_20%,#86efac33,transparent_36%),radial-gradient(circle_at_85%_0%,#67e8f933,transparent_44%),linear-gradient(140deg,#f7fff8_0%,#edf8ff_60%,#f2fff7_100%)] px-4 py-12 flex items-center">
      <div className="mx-auto w-full max-w-5xl grid gap-8 lg:grid-cols-[1.2fr_1fr]">
        <section className="rounded-3xl border border-emerald-100 bg-white/85 backdrop-blur-xl p-8 md:p-10 shadow-[0_28px_80px_rgba(16,185,129,0.18)]">
          <p className="inline-flex rounded-full border border-emerald-200 bg-emerald-50 px-4 py-1 text-sm font-semibold text-emerald-700">
            Plataforma premium para nutricionistas
          </p>
          <h1 className="mt-5 text-4xl font-black tracking-tight text-zinc-900">
            Bem-vinda de volta ao NutrIA Pro
          </h1>
          <p className="mt-4 text-zinc-600 text-lg">
            Acesse seu painel com secretária IA, chat omnicanal e operação nutricional completa.
          </p>
          <div className="mt-8 grid gap-3 sm:grid-cols-2">
            <div className="rounded-2xl border border-zinc-200 bg-white p-4">
              <p className="font-semibold text-zinc-900">Atendimento centralizado</p>
              <p className="text-sm text-zinc-600">WhatsApp, Instagram, Telegram e API em um único fluxo.</p>
            </div>
            <div className="rounded-2xl border border-zinc-200 bg-white p-4">
              <p className="font-semibold text-zinc-900">Operação contínua 24h</p>
              <p className="text-sm text-zinc-600">Seu sistema atua como uma equipe completa de suporte, agenda e relacionamento.</p>
            </div>
          </div>
        </section>

        <form
          onSubmit={handleSubmit}
          className="rounded-3xl border border-zinc-200 bg-white/95 backdrop-blur-xl p-8 shadow-[0_24px_64px_rgba(15,23,42,0.12)] flex flex-col gap-5"
        >
          <h2 className="text-2xl font-bold text-zinc-900">Login Nutricionista</h2>
          <input
            type="email"
            placeholder="E-mail"
            className="rounded-xl px-4 py-3 border border-zinc-200 bg-zinc-50 focus:outline-none focus:ring-2 focus:ring-emerald-300"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
          />
          <input
            type="password"
            placeholder="Senha"
            className="rounded-xl px-4 py-3 border border-zinc-200 bg-zinc-50 focus:outline-none focus:ring-2 focus:ring-emerald-300"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />
          {error && <div className="rounded-lg border border-red-200 bg-red-50 p-3 text-sm text-red-700">{error}</div>}
          <button
            disabled={loading}
            type="submit"
            className="rounded-xl bg-emerald-600 hover:bg-emerald-700 disabled:opacity-60 text-white px-6 py-3 font-semibold transition-all hover:-translate-y-0.5"
          >
            {loading ? "Entrando..." : "Entrar"}
          </button>
          <Link href="/nutricionista/cadastro?trial=1" className="text-center text-sm font-semibold text-emerald-700 hover:text-emerald-800">
            Solicitar acesso trial
          </Link>
        </form>
      </div>
    </div>
  );
}
