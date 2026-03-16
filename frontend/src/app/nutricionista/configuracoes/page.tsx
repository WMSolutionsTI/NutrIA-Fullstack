"use client";
import React, { useState } from "react";

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
  React.useEffect(() => {
    async function fetchConfig() {
      try {
        const { getConfiguracoesNutri } = await import("@/lib/api");
        const data = await getConfiguracoesNutri();
        setForm((prev) => ({ ...prev, ...data }));
      } catch (err) {
        // Ignorar erro ou mostrar mensagem
      }
    }
    fetchConfig();
  }, []);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setMsg("");
    try {
      // Chamada real de API para salvar configurações
      const { api } = await import("@/lib/api");
      await api("/nutricionista/configuracoes", {
        method: "POST",
        body: JSON.stringify(form),
      });
      setMsg("Configurações salvas com sucesso!");
    } catch (err: any) {
      setMsg("Erro ao salvar configurações: " + (err?.message || "Erro desconhecido"));
    }
  };

  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-gradient-to-br from-emerald-100 via-white to-blue-100 dark:from-zinc-900 dark:via-black dark:to-zinc-800 px-4 py-12">
      <form onSubmit={handleSubmit} className="bg-white dark:bg-zinc-900 rounded-xl shadow-lg p-8 w-full max-w-2xl flex flex-col gap-6 border border-emerald-100 dark:border-zinc-800">
        <h1 className="text-3xl font-bold text-center text-emerald-700 dark:text-emerald-300 mb-2">Configurações</h1>
        <input name="nome" type="text" placeholder="Nome completo" className="rounded px-4 py-3 border border-zinc-200 dark:border-zinc-700 bg-zinc-50 dark:bg-zinc-800" value={form.nome} onChange={handleChange} />
        <input name="email" type="email" placeholder="E-mail" className="rounded px-4 py-3 border border-zinc-200 dark:border-zinc-700 bg-zinc-50 dark:bg-zinc-800" value={form.email} onChange={handleChange} />
        <input name="telefone" type="tel" placeholder="Telefone" className="rounded px-4 py-3 border border-zinc-200 dark:border-zinc-700 bg-zinc-50 dark:bg-zinc-800" value={form.telefone} onChange={handleChange} />
        <input name="especialidade" type="text" placeholder="Especialidade" className="rounded px-4 py-3 border border-zinc-200 dark:border-zinc-700 bg-zinc-50 dark:bg-zinc-800" value={form.especialidade} onChange={handleChange} />
        <textarea name="prompt" placeholder="Prompt/contexto da secretária virtual" className="rounded px-4 py-3 border border-zinc-200 dark:border-zinc-700 bg-zinc-50 dark:bg-zinc-800" value={form.prompt} onChange={handleChange} />
        <input name="horario" type="text" placeholder="Horário de atendimento" className="rounded px-4 py-3 border border-zinc-200 dark:border-zinc-700 bg-zinc-50 dark:bg-zinc-800" value={form.horario} onChange={handleChange} />
        <input name="mensagemBoasVindas" type="text" placeholder="Mensagem de boas-vindas" className="rounded px-4 py-3 border border-zinc-200 dark:border-zinc-700 bg-zinc-50 dark:bg-zinc-800" value={form.mensagemBoasVindas} onChange={handleChange} />
        <input name="canais" type="text" placeholder="Canais conectados" className="rounded px-4 py-3 border border-zinc-200 dark:border-zinc-700 bg-zinc-50 dark:bg-zinc-800" value={form.canais} onChange={handleChange} />
        {msg && <div className="text-green-600 text-sm text-center">{msg}</div>}
        <button type="submit" className="rounded-full bg-emerald-500 hover:bg-emerald-600 text-white px-6 py-3 font-semibold shadow transition-colors">Salvar configurações</button>
      </form>
    </div>
  );
}
