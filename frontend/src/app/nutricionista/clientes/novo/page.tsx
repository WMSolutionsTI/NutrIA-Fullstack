"use client";

import React, { useState } from "react";
import Link from "next/link";

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
    if (!form.nome || !form.email) {
      setError("Nome e e-mail são obrigatórios.");
      return;
    }
    setError("");
    alert("Cliente cadastrado (simulado): " + JSON.stringify(form, null, 2));
  };

  return (
    <div className="mx-auto w-full max-w-3xl space-y-6">
      <section className="rounded-3xl border border-emerald-100 bg-white p-7 shadow-sm">
        <h1 className="text-3xl font-black text-zinc-900">Novo Cliente</h1>
        <p className="mt-2 text-zinc-600">
          Cadastre o cliente para iniciar atendimento, agenda e automações de relacionamento.
        </p>
      </section>

      <form onSubmit={handleSubmit} className="rounded-2xl border border-zinc-200 bg-white p-6 shadow-sm">
        <div className="grid gap-4 md:grid-cols-2">
          <input name="nome" type="text" placeholder="Nome completo" className="rounded-xl border border-zinc-200 bg-zinc-50 px-4 py-2.5 text-sm md:col-span-2" value={form.nome} onChange={handleChange} />
          <input name="email" type="email" placeholder="E-mail" className="rounded-xl border border-zinc-200 bg-zinc-50 px-4 py-2.5 text-sm" value={form.email} onChange={handleChange} />
          <input name="telefone" type="tel" placeholder="Telefone" className="rounded-xl border border-zinc-200 bg-zinc-50 px-4 py-2.5 text-sm" value={form.telefone} onChange={handleChange} />
          <input name="nascimento" type="date" className="rounded-xl border border-zinc-200 bg-zinc-50 px-4 py-2.5 text-sm" value={form.nascimento} onChange={handleChange} />
          <textarea name="observacoes" placeholder="Observações" className="h-28 rounded-xl border border-zinc-200 bg-zinc-50 px-4 py-2.5 text-sm md:col-span-2" value={form.observacoes} onChange={handleChange} />
        </div>
        {error && <div className="mt-4 rounded-xl bg-rose-50 px-3 py-2 text-sm font-semibold text-rose-700">{error}</div>}
        <div className="mt-5 flex flex-wrap gap-3">
          <button type="submit" className="rounded-xl bg-emerald-500 px-5 py-2.5 text-sm font-semibold text-white hover:bg-emerald-600">
            Cadastrar cliente
          </button>
          <Link href="/nutricionista/clientes" className="rounded-xl border border-zinc-300 bg-white px-5 py-2.5 text-sm font-semibold text-zinc-700 hover:bg-zinc-50">
            Voltar para clientes
          </Link>
        </div>
      </form>
    </div>
  );
}
