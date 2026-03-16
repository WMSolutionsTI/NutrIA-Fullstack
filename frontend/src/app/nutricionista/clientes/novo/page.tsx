"use client";
import React, { useState } from "react";

export default function NovoCliente() {
  const [form, setForm] = useState({
    nome: "",
    email: "",
    telefone: "",
    nascimento: "",
    observacoes: "",
  });
  const [error, setError] = useState("");

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    // TODO: Chamada real de API para cadastro
    if (!form.nome || !form.email) {
      setError("Nome e e-mail são obrigatórios.");
      return;
    }
    setError("");
    alert("Cliente cadastrado (simulado): " + JSON.stringify(form, null, 2));
  };

  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-gradient-to-br from-emerald-100 via-white to-blue-100 dark:from-zinc-900 dark:via-black dark:to-zinc-800 px-4 py-12">
      <form onSubmit={handleSubmit} className="bg-white dark:bg-zinc-900 rounded-xl shadow-lg p-8 w-full max-w-lg flex flex-col gap-6 border border-emerald-100 dark:border-zinc-800">
        <h1 className="text-3xl font-bold text-center text-emerald-700 dark:text-emerald-300 mb-2">Novo Cliente</h1>
        <input name="nome" type="text" placeholder="Nome completo" className="rounded px-4 py-3 border border-zinc-200 dark:border-zinc-700 bg-zinc-50 dark:bg-zinc-800" value={form.nome} onChange={handleChange} />
        <input name="email" type="email" placeholder="E-mail" className="rounded px-4 py-3 border border-zinc-200 dark:border-zinc-700 bg-zinc-50 dark:bg-zinc-800" value={form.email} onChange={handleChange} />
        <input name="telefone" type="tel" placeholder="Telefone" className="rounded px-4 py-3 border border-zinc-200 dark:border-zinc-700 bg-zinc-50 dark:bg-zinc-800" value={form.telefone} onChange={handleChange} />
        <input name="nascimento" type="date" placeholder="Data de nascimento" className="rounded px-4 py-3 border border-zinc-200 dark:border-zinc-700 bg-zinc-50 dark:bg-zinc-800" value={form.nascimento} onChange={handleChange} />
        <textarea name="observacoes" placeholder="Observações (opcional)" className="rounded px-4 py-3 border border-zinc-200 dark:border-zinc-700 bg-zinc-50 dark:bg-zinc-800" value={form.observacoes} onChange={handleChange} />
        {error && <div className="text-red-600 text-sm text-center">{error}</div>}
        <button type="submit" className="rounded-full bg-emerald-500 hover:bg-emerald-600 text-white px-6 py-3 font-semibold shadow transition-colors">Cadastrar</button>
      </form>
    </div>
  );
}
