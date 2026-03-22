"use client";

import React, { useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";

import { createAgendaEvento } from "@/lib/api/agenda";
import { ApiError } from "@/lib/api/client";

export default function NovaConsulta() {
  const router = useRouter();
  const [form, setForm] = useState({
    clienteId: "",
    data: "",
    hora: "",
    observacoes: "",
    titulo: "",
  });
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!form.data || !form.hora || !form.titulo) {
      setError("Preencha todos os campos obrigatórios.");
      return;
    }
    setLoading(true);
    try {
      const inicio = new Date(`${form.data}T${form.hora}:00`);
      const fim = new Date(inicio.getTime() + 60 * 60 * 1000);
      await createAgendaEvento({
        titulo: form.titulo,
        descricao: form.observacoes || undefined,
        inicio_em: inicio.toISOString(),
        fim_em: fim.toISOString(),
        cliente_id: form.clienteId ? Number(form.clienteId) : undefined,
      });
      router.push("/nutricionista/agenda");
    } catch (e) {
      const detail = e instanceof ApiError ? e.detail : "Erro ao cadastrar consulta.";
      setError(detail);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="mx-auto w-full max-w-3xl space-y-6">
      <section className="rounded-3xl border border-emerald-100 bg-white p-7 shadow-sm">
        <h1 className="text-3xl font-black text-zinc-900">Nova consulta</h1>
        <p className="mt-2 text-zinc-600">
          Registre atendimento com dados completos para automações de confirmação e lembrete.
        </p>
      </section>

      <form onSubmit={handleSubmit} className="rounded-2xl border border-zinc-200 bg-white p-6 shadow-sm">
        <div className="grid gap-4 md:grid-cols-2">
          <div className="md:col-span-2">
            <label className="mb-1 block text-sm font-semibold text-zinc-700">Cliente</label>
            <input
              name="clienteId"
              type="number"
              placeholder="ID do cliente"
              className="w-full rounded-xl border border-zinc-200 bg-zinc-50 px-4 py-2.5 text-sm"
              value={form.clienteId}
              onChange={handleChange}
            />
          </div>
          <div className="md:col-span-2">
            <label className="mb-1 block text-sm font-semibold text-zinc-700">Título da consulta</label>
            <input
              name="titulo"
              type="text"
              placeholder="Ex.: Consulta de retorno"
              className="w-full rounded-xl border border-zinc-200 bg-zinc-50 px-4 py-2.5 text-sm"
              value={form.titulo}
              onChange={handleChange}
            />
          </div>
          <div>
            <label className="mb-1 block text-sm font-semibold text-zinc-700">Data</label>
            <input
              name="data"
              type="date"
              className="w-full rounded-xl border border-zinc-200 bg-zinc-50 px-4 py-2.5 text-sm"
              value={form.data}
              onChange={handleChange}
            />
          </div>
          <div>
            <label className="mb-1 block text-sm font-semibold text-zinc-700">Hora</label>
            <input
              name="hora"
              type="time"
              className="w-full rounded-xl border border-zinc-200 bg-zinc-50 px-4 py-2.5 text-sm"
              value={form.hora}
              onChange={handleChange}
            />
          </div>
          <div className="md:col-span-2">
            <label className="mb-1 block text-sm font-semibold text-zinc-700">Observações</label>
            <textarea
              name="observacoes"
              placeholder="Observações da consulta"
              className="h-28 w-full rounded-xl border border-zinc-200 bg-zinc-50 px-4 py-2.5 text-sm"
              value={form.observacoes}
              onChange={handleChange}
            />
          </div>
        </div>

        {error && <div className="mt-4 rounded-xl bg-rose-50 px-3 py-2 text-sm font-semibold text-rose-700">{error}</div>}

        <div className="mt-5 flex flex-wrap gap-3">
          <button type="submit" disabled={loading} className="rounded-xl bg-emerald-500 px-5 py-2.5 text-sm font-semibold text-white hover:bg-emerald-600 disabled:opacity-60">
            {loading ? "Cadastrando..." : "Cadastrar consulta"}
          </button>
          <Link href="/nutricionista/agenda" className="rounded-xl border border-zinc-300 bg-white px-5 py-2.5 text-sm font-semibold text-zinc-700 hover:bg-zinc-50">
            Voltar para agenda
          </Link>
        </div>
      </form>
    </div>
  );
}
