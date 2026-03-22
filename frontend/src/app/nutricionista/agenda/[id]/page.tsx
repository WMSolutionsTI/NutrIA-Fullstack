"use client";

import Link from "next/link";
import { useEffect, useState } from "react";

import { ApiError } from "@/lib/api/client";
import { AgendaEvento, deleteAgendaEvento, getAgendaEvento } from "@/lib/api/agenda";

export default function ConsultaDetalhe({ params }: { params: { id: string } }) {
  const [consulta, setConsulta] = useState<AgendaEvento | null>(null);
  const [erro, setErro] = useState("");

  async function carregar() {
    try {
      const data = await getAgendaEvento(Number(params.id));
      setConsulta(data);
    } catch (e) {
      const detail = e instanceof ApiError ? e.detail : "Falha ao carregar consulta.";
      setErro(detail);
    }
  }

  async function cancelar() {
    if (!consulta) return;
    try {
      await deleteAgendaEvento(consulta.id);
      window.location.href = "/nutricionista/agenda";
    } catch (e) {
      const detail = e instanceof ApiError ? e.detail : "Falha ao cancelar consulta.";
      setErro(detail);
    }
  }

  useEffect(() => {
    carregar();
  }, [params.id]);

  const dataInicio = consulta ? new Date(consulta.inicio_em) : null;

  return (
    <div className="mx-auto w-full max-w-4xl space-y-6">
      <section className="rounded-3xl border border-emerald-100 bg-white p-7 shadow-sm">
        <h1 className="text-3xl font-black text-zinc-900">Consulta {consulta ? `#${consulta.id}` : ""}</h1>
        <p className="mt-2 text-zinc-600">
          Gerencie status e informações da consulta para manter a régua de atendimento atualizada.
        </p>
      </section>

      <section className="rounded-2xl border border-zinc-200 bg-white p-6 shadow-sm">
        {erro && (
          <div className="mb-4 rounded-xl bg-rose-50 px-3 py-2 text-sm font-semibold text-rose-700">{erro}</div>
        )}
        <div className="grid gap-4 md:grid-cols-2">
          <article className="rounded-xl border border-zinc-200 bg-zinc-50 p-4">
            <p className="text-xs font-semibold uppercase tracking-wide text-zinc-500">Data</p>
            <p className="mt-1 text-lg font-bold text-zinc-900">{dataInicio ? dataInicio.toLocaleDateString("pt-BR") : "-"}</p>
          </article>
          <article className="rounded-xl border border-zinc-200 bg-zinc-50 p-4">
            <p className="text-xs font-semibold uppercase tracking-wide text-zinc-500">Hora</p>
            <p className="mt-1 text-lg font-bold text-zinc-900">
              {dataInicio ? dataInicio.toLocaleTimeString("pt-BR", { hour: "2-digit", minute: "2-digit" }) : "-"}
            </p>
          </article>
          <article className="rounded-xl border border-zinc-200 bg-zinc-50 p-4">
            <p className="text-xs font-semibold uppercase tracking-wide text-zinc-500">Status</p>
            <span className="mt-1 inline-block rounded-full bg-emerald-100 px-3 py-1 text-sm font-semibold text-emerald-700">
              {consulta?.status ?? "-"}
            </span>
          </article>
          <article className="rounded-xl border border-zinc-200 bg-zinc-50 p-4">
            <p className="text-xs font-semibold uppercase tracking-wide text-zinc-500">Observações</p>
            <p className="mt-1 text-sm text-zinc-700">{consulta?.descricao ?? "-"}</p>
          </article>
        </div>

        <div className="mt-5 flex flex-wrap gap-3">
          <button disabled className="rounded-xl bg-zinc-300 px-4 py-2 text-sm font-semibold text-zinc-600">
            Editar
          </button>
          <button onClick={cancelar} className="rounded-xl bg-rose-500 px-4 py-2 text-sm font-semibold text-white hover:bg-rose-600">
            Cancelar
          </button>
          <Link href="/nutricionista/agenda" className="rounded-xl border border-zinc-300 bg-white px-4 py-2 text-sm font-semibold text-zinc-700 hover:bg-zinc-50">
            Voltar para agenda
          </Link>
        </div>
      </section>
    </div>
  );
}
