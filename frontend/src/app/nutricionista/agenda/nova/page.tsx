"use client";
import React, { useState } from "react";

export default function NovaConsulta() {
  const [form, setForm] = useState({
    cliente: "",
    data: "",
    hora: "",
    observacoes: "",
  });
  const [error, setError] = useState("");

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    // TODO: Chamada real de API para cadastro
    if (!form.cliente || !form.data || !form.hora) {
      setError("Preencha todos os campos obrigatórios.");
      return;
    }
    setError("");
    alert("Consulta cadastrada (simulado): " + JSON.stringify(form, null, 2));
  };

  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-gradient-to-br from-emerald-100 via-white to-blue-100 dark:from-zinc-900 dark:via-black dark:to-zinc-800 px-4 py-12">
      <form onSubmit={handleSubmit} className="bg-white dark:bg-zinc-900 rounded-xl shadow-lg p-8 w-full max-w-lg flex flex-col gap-6 border border-emerald-100 dark:border-zinc-800">
        <h1 className="text-3xl font-bold text-center text-emerald-700 dark:text-emerald-300 mb-2">Nova Consulta</h1>
        <input name="cliente" type="text" placeholder="Nome do cliente" className="rounded px-4 py-3 border border-zinc-200 dark:border-zinc-700 bg-zinc-50 dark:bg-zinc-800" value={form.cliente} onChange={handleChange} />
        <input name="data" type="date" placeholder="Data" className="rounded px-4 py-3 border border-zinc-200 dark:border-zinc-700 bg-zinc-50 dark:bg-zinc-800" value={form.data} onChange={handleChange} />
        <input name="hora" type="time" placeholder="Hora" className="rounded px-4 py-3 border border-zinc-200 dark:border-zinc-700 bg-zinc-50 dark:bg-zinc-800" value={form.hora} onChange={handleChange} />
        <textarea name="observacoes" placeholder="Observações (opcional)" className="rounded px-4 py-3 border border-zinc-200 dark:border-zinc-700 bg-zinc-50 dark:bg-zinc-800" value={form.observacoes} onChange={handleChange} />
        {error && <div className="text-red-600 text-sm text-center">{error}</div>}
        <button type="submit" className="rounded-full bg-emerald-500 hover:bg-emerald-600 text-white px-6 py-3 font-semibold shadow transition-colors">Cadastrar</button>
      </form>
    </div>
  );
}
