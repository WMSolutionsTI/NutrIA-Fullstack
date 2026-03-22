"use client";
import Link from "next/link";
import React, { useEffect, useState } from "react";

import { ApiError } from "@/lib/api/client";
import { AgendaEvento, deleteAgendaEvento, listAgendaEventos } from "@/lib/api/agenda";

interface ConsultaView {
  id: number;
  cliente: string;
  data: string;
  hora: string;
  status: string;
}

function toView(evento: AgendaEvento): ConsultaView {
  const date = new Date(evento.inicio_em);
  return {
    id: evento.id,
    cliente: evento.cliente_id ? `Cliente #${evento.cliente_id}` : "Cliente não vinculado",
    data: Number.isNaN(date.getTime()) ? "-" : date.toLocaleDateString("pt-BR"),
    hora: Number.isNaN(date.getTime()) ? "-" : date.toLocaleTimeString("pt-BR", { hour: "2-digit", minute: "2-digit" }),
    status: evento.status,
  };
}

export default function Agenda() {
  const [consultas, setConsultas] = useState<ConsultaView[]>([]);
  const [busca, setBusca] = useState("");
  const [erro, setErro] = useState("");
  const [loading, setLoading] = useState(true);

  const filtradas = consultas.filter(c =>
    c.cliente.toLowerCase().includes(busca.toLowerCase())
  );

  async function carregarConsultas() {
    setLoading(true);
    setErro("");
    try {
      const data = await listAgendaEventos();
      setConsultas(data.map(toView));
    } catch (e) {
      const detail = e instanceof ApiError ? e.detail : "Falha ao carregar agenda.";
      setErro(detail);
    } finally {
      setLoading(false);
    }
  }

  async function handleCancelar(consultaId: number) {
    try {
      await deleteAgendaEvento(consultaId);
      await carregarConsultas();
    } catch (e) {
      const detail = e instanceof ApiError ? e.detail : "Falha ao cancelar evento.";
      setErro(detail);
    }
  }

  useEffect(() => {
    carregarConsultas();
  }, []);

  return (
    <div className="mx-auto w-full max-w-6xl space-y-6">
      <section className="rounded-3xl border border-emerald-100 bg-white p-7 shadow-sm">
        <h1 className="text-3xl font-black text-zinc-900">Agenda de Consultas</h1>
        <p className="mt-2 text-zinc-600">
          Controle total dos atendimentos com visão de confirmação, pendências e ações rápidas.
        </p>
      </section>

      <section className="rounded-2xl border border-zinc-200 bg-white p-6 shadow-sm">
        <div className="mb-5 flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
          <input
            type="text"
            placeholder="Buscar por cliente"
            className="w-full rounded-xl border border-zinc-200 bg-zinc-50 px-4 py-2.5 text-sm md:max-w-sm"
            value={busca}
            onChange={(e) => setBusca(e.target.value)}
          />
          <Link href="/nutricionista/agenda/nova" className="rounded-xl bg-emerald-500 px-4 py-2.5 text-sm font-semibold text-white hover:bg-emerald-600">
            Nova consulta
          </Link>
        </div>

        <div className="overflow-x-auto rounded-xl border border-zinc-200">
          {erro && (
            <div className="border-b border-rose-100 bg-rose-50 px-4 py-3 text-sm font-medium text-rose-700">{erro}</div>
          )}
          <table className="min-w-full text-left text-sm">
            <thead className="bg-zinc-100">
              <tr className="text-zinc-700">
                <th className="py-3 px-4">Cliente</th>
                <th className="py-3 px-4">Data</th>
                <th className="py-3 px-4">Hora</th>
                <th className="py-3 px-4">Status</th>
                <th className="py-3 px-4">Ações</th>
              </tr>
            </thead>
            <tbody>
              {loading && (
                <tr>
                  <td colSpan={5} className="py-4 px-4 text-center text-zinc-500">
                    Carregando agenda...
                  </td>
                </tr>
              )}
              {filtradas.map((consulta) => (
                <tr key={consulta.id} className="border-t border-zinc-200 text-zinc-700">
                  <td className="py-2 px-4">{consulta.cliente}</td>
                  <td className="py-2 px-4">{consulta.data}</td>
                  <td className="py-2 px-4">{consulta.hora}</td>
                  <td className="py-2 px-4">
                    <span
                      className={`rounded-full px-2.5 py-1 text-xs font-semibold ${
                        consulta.status === "Confirmada"
                          ? "bg-emerald-100 text-emerald-700"
                          : "bg-amber-100 text-amber-700"
                      }`}
                    >
                      {consulta.status}
                    </span>
                  </td>
                  <td className="py-2 px-4">
                    <Link className="mr-3 font-semibold text-cyan-700 hover:text-cyan-800" href={`/nutricionista/agenda/${consulta.id}`}>
                      Ver
                    </Link>
                    <button className="mr-3 font-semibold text-zinc-400" disabled>Editar</button>
                    <button onClick={() => handleCancelar(consulta.id)} className="font-semibold text-rose-700 hover:text-rose-800">Cancelar</button>
                  </td>
                </tr>
              ))}
              {!loading && filtradas.length === 0 && (
                <tr>
                  <td colSpan={5} className="py-4 px-4 text-center text-zinc-500">
                    Nenhuma consulta encontrada.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </section>
    </div>
  );
}
