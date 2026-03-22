"use client";

import React, { useState } from "react";
import { useRouter } from "next/navigation";

export default function AdminLogin() {
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!email || !password) {
      setError("Preencha e-mail e senha.");
      return;
    }
    setError("");
    router.push("/admin/dashboard");
  };

  return (
    <div className="min-h-screen bg-[radial-gradient(circle_at_20%_20%,#67e8f933,transparent_35%),radial-gradient(circle_at_80%_0%,#86efac33,transparent_40%),linear-gradient(140deg,#f7fbff_0%,#f3fff8_100%)] flex items-center px-4">
      <div className="mx-auto w-full max-w-5xl grid gap-8 lg:grid-cols-[1.2fr_1fr]">
        <section className="rounded-3xl border border-zinc-200 bg-white/90 p-8 shadow-[0_28px_80px_rgba(15,23,42,0.12)]">
          <p className="inline-flex rounded-full border border-cyan-200 bg-cyan-50 px-4 py-1 text-xs font-semibold text-cyan-800">
            Painel Executivo NutrIA Pro
          </p>
          <h1 className="mt-5 text-4xl font-black text-zinc-900">Controle central da operação SaaS</h1>
          <p className="mt-3 text-zinc-600">
            Acompanhe performance comercial, saúde financeira, retenção de clientes e escala da plataforma em tempo real.
          </p>
          <div className="mt-8 grid sm:grid-cols-2 gap-4">
            <div className="rounded-2xl border border-zinc-200 bg-zinc-50 p-4">
              <p className="font-semibold text-zinc-900">Vendas e conversão</p>
              <p className="text-sm text-zinc-600">Insights acionáveis para acelerar crescimento.</p>
            </div>
            <div className="rounded-2xl border border-zinc-200 bg-zinc-50 p-4">
              <p className="font-semibold text-zinc-900">Operação 24h</p>
              <p className="text-sm text-zinc-600">Visão estratégica da máquina de atendimento inteligente.</p>
            </div>
          </div>
        </section>

        <form
          onSubmit={handleSubmit}
          className="rounded-3xl border border-zinc-200 bg-white p-8 shadow-[0_24px_64px_rgba(15,23,42,0.10)] flex flex-col gap-5"
        >
          <h2 className="text-2xl font-bold text-zinc-900">Login Admin</h2>
          <input
            type="email"
            placeholder="E-mail"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            className="rounded-xl border border-zinc-200 bg-zinc-50 px-4 py-3 focus:outline-none focus:ring-2 focus:ring-cyan-300"
          />
          <input
            type="password"
            placeholder="Senha"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className="rounded-xl border border-zinc-200 bg-zinc-50 px-4 py-3 focus:outline-none focus:ring-2 focus:ring-cyan-300"
          />
          {error && <div className="rounded-lg border border-red-200 bg-red-50 p-3 text-sm text-red-700">{error}</div>}
          <button
            type="submit"
            className="rounded-xl bg-zinc-900 hover:bg-zinc-800 text-white px-5 py-3 font-semibold transition-all hover:-translate-y-0.5"
          >
            Entrar no painel
          </button>
        </form>
      </div>
    </div>
  );
}
