"use client";

import React, { useState } from "react";

interface Campanha {
  id: string;
  titulo: string;
  mensagem: string;
  data: string;
  status: string;
}

const MOCK_CAMPANHAS: Campanha[] = [
  { id: "1", titulo: "Campanha de Retorno", mensagem: "Olá! Venha agendar sua próxima consulta.", data: "2026-03-10", status: "Enviada" },
  { id: "2", titulo: "Campanha de Aniversário", mensagem: "Feliz aniversário!", data: "2026-03-12", status: "Agendada" },
];

export default function Campanhas() {
  const [campanhas] = useState<Campanha[]>(MOCK_CAMPANHAS);
  const [busca, setBusca] = useState("");

  const filtradas = campanhas.filter(c =>
    c.titulo.toLowerCase().includes(busca.toLowerCase())
  );

  return (
    <div className="mx-auto w-full max-w-6xl space-y-6">
      <section className="rounded-3xl border border-emerald-100 bg-white p-7 shadow-sm">
        <h1 className="text-3xl font-black text-zinc-900">Campanhas e Retenção</h1>
        <p className="mt-2 text-zinc-600">
          Dispare campanhas com consistência comercial e acompanhe performance de relacionamento.
        </p>
      </section>

      <section className="rounded-2xl border border-zinc-200 bg-white p-6 shadow-sm">
        <div className="mb-5 flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
          <input
            type="text"
            placeholder="Buscar por título"
            className="w-full rounded-xl border border-zinc-200 bg-zinc-50 px-4 py-2.5 text-sm md:max-w-sm"
            value={busca}
            onChange={(e) => setBusca(e.target.value)}
          />
          <button className="rounded-xl bg-emerald-500 px-4 py-2.5 text-sm font-semibold text-white hover:bg-emerald-600">
            Nova campanha
          </button>
        </div>

        <div className="overflow-x-auto rounded-xl border border-zinc-200">
          <table className="min-w-full text-left text-sm">
            <thead className="bg-zinc-100">
              <tr className="text-zinc-700">
                <th className="py-3 px-4">Título</th>
                <th className="py-3 px-4">Mensagem</th>
                <th className="py-3 px-4">Data</th>
                <th className="py-3 px-4">Status</th>
                <th className="py-3 px-4">Ações</th>
              </tr>
            </thead>
            <tbody>
              {filtradas.map((campanha) => (
                <tr key={campanha.id} className="border-t border-zinc-200 text-zinc-700">
                  <td className="py-2 px-4">{campanha.titulo}</td>
                  <td className="py-2 px-4">{campanha.mensagem}</td>
                  <td className="py-2 px-4">{campanha.data}</td>
                  <td className="py-2 px-4">
                    <span
                      className={`rounded-full px-2.5 py-1 text-xs font-semibold ${
                        campanha.status === "Enviada" ? "bg-emerald-100 text-emerald-700" : "bg-cyan-100 text-cyan-700"
                      }`}
                    >
                      {campanha.status}
                    </span>
                  </td>
                  <td className="py-2 px-4">
                    <button className="mr-3 font-semibold text-cyan-700 hover:text-cyan-800">Ver</button>
                    <button className="mr-3 font-semibold text-emerald-700 hover:text-emerald-800">Editar</button>
                    <button className="font-semibold text-rose-700 hover:text-rose-800">Excluir</button>
                  </td>
                </tr>
              ))}
              {filtradas.length === 0 && (
                <tr>
                  <td colSpan={5} className="py-4 px-4 text-center text-zinc-500">Nenhuma campanha encontrada.</td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </section>
    </div>
  );
}
