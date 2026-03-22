"use client";

import Link from "next/link";
import React, { useState } from "react";

import { ApiError } from "@/lib/api/client";
import { solicitarTrial } from "@/lib/api/auth";

export default function NutriCadastro() {
  const [form, setForm] = useState({
    nome: "",
    email: "",
    telefone: "",
  });
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [requested, setRequested] = useState(false);

  function handleChange(e: React.ChangeEvent<HTMLInputElement>) {
    setForm({ ...form, [e.target.name]: e.target.value });
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!form.nome || !form.email || !form.telefone) {
      setError("Preencha nome, telefone e e-mail.");
      return;
    }

    try {
      setLoading(true);
      setError("");
      await solicitarTrial(form);
      setRequested(true);
    } catch (err) {
      if (err instanceof ApiError) {
        setError(err.detail);
      } else {
        setError("Não foi possível solicitar seu cadastro de trial.");
      }
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="min-h-screen bg-[radial-gradient(circle_at_15%_20%,#c6f6d544,transparent_35%),radial-gradient(circle_at_85%_0%,#99f6e444,transparent_45%),linear-gradient(130deg,#f4fff7_0%,#eef9ff_55%,#f8fff9_100%)] px-4 py-10 md:py-16">
      <div className="mx-auto max-w-6xl grid gap-8 lg:grid-cols-[1.2fr_1fr]">
        <section className="rounded-3xl border border-emerald-100 bg-white/90 backdrop-blur-xl shadow-[0_24px_80px_rgba(16,185,129,0.12)] p-8 md:p-10">
          <p className="inline-flex items-center rounded-full border border-emerald-200 bg-emerald-50 px-4 py-1 text-sm font-semibold text-emerald-700">
            Ativação da Plataforma NutrIA Pro
          </p>
          <h1 className="mt-5 text-3xl md:text-4xl font-black text-zinc-900">
            Solicite seu acesso de trial
          </h1>
          <p className="mt-3 text-zinc-600">
            Informe apenas seus dados principais. O worker de cadastros enviará por e-mail uma senha temporária para o primeiro acesso.
          </p>
          <div className="mt-6 rounded-2xl border border-cyan-200 bg-cyan-50 p-4 text-cyan-900">
            No primeiro login, você trocará a senha e em seguida completará seu cadastro com CPF obrigatório e endereço.
          </div>
          {requested && (
            <div className="mt-4 rounded-2xl border border-blue-200 bg-blue-50 p-4 text-blue-900">
              Solicitação recebida. Verifique seu e-mail para acessar com a senha temporária.
            </div>
          )}
        </section>

        <form
          onSubmit={handleSubmit}
          className="rounded-3xl border border-zinc-200/80 bg-white/95 backdrop-blur-xl shadow-[0_24px_80px_rgba(15,23,42,0.10)] p-7 md:p-8 flex flex-col gap-5"
        >
          <h2 className="text-2xl font-bold text-zinc-900">Cadastro inicial</h2>
          <input name="nome" type="text" placeholder="Nome completo" className="rounded-xl px-4 py-3 border border-zinc-200 bg-zinc-50 focus:outline-none focus:ring-2 focus:ring-emerald-300" value={form.nome} onChange={handleChange} />
          <input name="telefone" type="tel" placeholder="Telefone com WhatsApp" className="rounded-xl px-4 py-3 border border-zinc-200 bg-zinc-50 focus:outline-none focus:ring-2 focus:ring-emerald-300" value={form.telefone} onChange={handleChange} />
          <input name="email" type="email" placeholder="E-mail profissional" className="rounded-xl px-4 py-3 border border-zinc-200 bg-zinc-50 focus:outline-none focus:ring-2 focus:ring-emerald-300" value={form.email} onChange={handleChange} />

          {error && <div className="rounded-lg border border-red-200 bg-red-50 p-3 text-sm text-red-700">{error}</div>}

          <div className="flex gap-3 justify-between pt-2">
            <Link href="/nutricionista/login" className="rounded-xl px-4 py-2.5 border border-zinc-200 bg-white text-zinc-700 hover:bg-zinc-50 transition-colors">
              Já tenho acesso
            </Link>
            <button
              disabled={loading}
              type="submit"
              className="ml-auto rounded-xl px-5 py-2.5 bg-emerald-600 hover:bg-emerald-700 text-white font-semibold disabled:opacity-60 transition-all hover:-translate-y-0.5"
            >
              {loading ? "Enviando..." : "Solicitar acesso trial"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
