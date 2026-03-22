"use client";

import React, { useState } from "react";

import { ApiError } from "@/lib/api/client";
import {
  desconectarGoogleIntegracao,
  getGoogleIntegracaoStatus,
  iniciarGoogleIntegracao,
} from "@/lib/api/agenda";

export default function Configuracoes() {
  const [form, setForm] = useState({
    nome: "",
    email: "",
    telefone: "",
    especialidade: "",
    prompt: "",
    horario: "",
    mensagemBoasVindas: "",
    canais: "",
  });
  const [msg, setMsg] = useState("");
  const [googleStatus, setGoogleStatus] = useState<{
    conectado: boolean;
    google_email?: string;
  }>({ conectado: false });
  const [loadingGoogle, setLoadingGoogle] = useState(false);

  async function carregarGoogleStatus() {
    try {
      const data = await getGoogleIntegracaoStatus();
      setGoogleStatus({ conectado: data.conectado, google_email: data.google_email });
    } catch {
      setGoogleStatus({ conectado: false });
    }
  }

  React.useEffect(() => {
    async function fetchConfig() {
      try {
        const { getConfiguracoesNutri } = await import("@/lib/api");
        const data = await getConfiguracoesNutri();
        setForm((prev) => ({ ...prev, ...data }));
      } catch {
        // fallback silencioso para manter tela acessível mesmo sem API pronta
      }
    }
    fetchConfig();
    carregarGoogleStatus();
  }, []);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setMsg("");
    try {
      const { api } = await import("@/lib/api");
      await api("/nutricionista/configuracoes", {
        method: "POST",
        body: JSON.stringify(form),
      });
      setMsg("Configurações salvas com sucesso.");
    } catch (err: any) {
      setMsg("Erro ao salvar configurações: " + (err?.message || "Erro desconhecido"));
    }
  };

  const conectarGoogle = async () => {
    setLoadingGoogle(true);
    try {
      const data = await iniciarGoogleIntegracao();
      window.location.href = data.auth_url;
    } catch (e) {
      const detail = e instanceof ApiError ? e.detail : "Erro ao iniciar integração Google.";
      setMsg(`Erro ao integrar Google: ${detail}`);
    } finally {
      setLoadingGoogle(false);
    }
  };

  const desconectarGoogle = async () => {
    setLoadingGoogle(true);
    try {
      await desconectarGoogleIntegracao();
      await carregarGoogleStatus();
      setMsg("Integração Google desconectada.");
    } catch (e) {
      const detail = e instanceof ApiError ? e.detail : "Erro ao desconectar Google.";
      setMsg(`Erro ao desconectar Google: ${detail}`);
    } finally {
      setLoadingGoogle(false);
    }
  };

  return (
    <div className="mx-auto w-full max-w-5xl space-y-6">
      <section className="rounded-3xl border border-emerald-100 bg-white p-7 shadow-sm">
        <h1 className="text-3xl font-black text-zinc-900">Configurações da Operação</h1>
        <p className="mt-2 text-zinc-600">
          Personalize identidade da secretária, regras de atendimento e canais conectados da sua conta.
        </p>
      </section>

      <form onSubmit={handleSubmit} className="rounded-2xl border border-zinc-200 bg-white p-6 shadow-sm">
        <div className="grid gap-4 md:grid-cols-2">
          <input name="nome" type="text" placeholder="Nome completo" className="rounded-xl border border-zinc-200 bg-zinc-50 px-4 py-2.5 text-sm" value={form.nome} onChange={handleChange} />
          <input name="email" type="email" placeholder="E-mail" className="rounded-xl border border-zinc-200 bg-zinc-50 px-4 py-2.5 text-sm" value={form.email} onChange={handleChange} />
          <input name="telefone" type="tel" placeholder="Telefone" className="rounded-xl border border-zinc-200 bg-zinc-50 px-4 py-2.5 text-sm" value={form.telefone} onChange={handleChange} />
          <input name="especialidade" type="text" placeholder="Especialidade" className="rounded-xl border border-zinc-200 bg-zinc-50 px-4 py-2.5 text-sm" value={form.especialidade} onChange={handleChange} />
          <input name="horario" type="text" placeholder="Horário de atendimento" className="rounded-xl border border-zinc-200 bg-zinc-50 px-4 py-2.5 text-sm" value={form.horario} onChange={handleChange} />
          <input name="canais" type="text" placeholder="Canais conectados" className="rounded-xl border border-zinc-200 bg-zinc-50 px-4 py-2.5 text-sm" value={form.canais} onChange={handleChange} />
          <input name="mensagemBoasVindas" type="text" placeholder="Mensagem de boas-vindas" className="rounded-xl border border-zinc-200 bg-zinc-50 px-4 py-2.5 text-sm md:col-span-2" value={form.mensagemBoasVindas} onChange={handleChange} />
          <textarea name="prompt" placeholder="Prompt completo da secretária virtual" className="h-32 rounded-xl border border-zinc-200 bg-zinc-50 px-4 py-2.5 text-sm md:col-span-2" value={form.prompt} onChange={handleChange} />
        </div>

        {msg && (
          <div className={`mt-4 rounded-xl px-3 py-2 text-sm font-semibold ${msg.startsWith("Erro") ? "bg-rose-50 text-rose-700" : "bg-emerald-50 text-emerald-700"}`}>
            {msg}
          </div>
        )}

        <button type="submit" className="mt-5 rounded-xl bg-emerald-500 px-5 py-2.5 text-sm font-semibold text-white hover:bg-emerald-600">
          Salvar configurações
        </button>
      </form>

      <section className="rounded-2xl border border-zinc-200 bg-white p-6 shadow-sm">
        <h2 className="text-xl font-black text-zinc-900">Google Agenda</h2>
        <p className="mt-1 text-sm text-zinc-600">
          Conecte sua conta Google para sincronizar consultas automaticamente.
        </p>
        <div className="mt-4 flex flex-wrap items-center gap-3">
          <span
            className={`rounded-full px-3 py-1 text-xs font-semibold ${
              googleStatus.conectado ? "bg-emerald-100 text-emerald-700" : "bg-amber-100 text-amber-700"
            }`}
          >
            {googleStatus.conectado ? `Conectado (${googleStatus.google_email ?? "Google"})` : "Não conectado"}
          </span>
          {!googleStatus.conectado ? (
            <button
              onClick={conectarGoogle}
              disabled={loadingGoogle}
              className="rounded-xl bg-cyan-600 px-4 py-2 text-sm font-semibold text-white hover:bg-cyan-700 disabled:opacity-60"
              type="button"
            >
              {loadingGoogle ? "Conectando..." : "Conectar Google Agenda"}
            </button>
          ) : (
            <button
              onClick={desconectarGoogle}
              disabled={loadingGoogle}
              className="rounded-xl border border-zinc-300 bg-white px-4 py-2 text-sm font-semibold text-zinc-700 hover:bg-zinc-50 disabled:opacity-60"
              type="button"
            >
              {loadingGoogle ? "Desconectando..." : "Desconectar"}
            </button>
          )}
        </div>
      </section>
    </div>
  );
}
