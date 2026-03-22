"use client";

import React, { useState } from "react";

interface Cobranca {
  id: string;
  cliente: string;
  valor: number;
  status: string;
  vencimento: string;
  link: string;
}

const MOCK_COBRANCAS: Cobranca[] = [
  { id: "1", cliente: "Maria Silva", valor: 200, status: "Paga", vencimento: "2026-03-10", link: "https://pagamento.com/1" },
  { id: "2", cliente: "João Souza", valor: 180, status: "Pendente", vencimento: "2026-03-20", link: "https://pagamento.com/2" },
];

export default function Cobrancas() {
  const [cobrancas] = useState<Cobranca[]>(MOCK_COBRANCAS);
  const [busca, setBusca] = useState("");

  const filtradas = cobrancas.filter(c =>
    c.cliente.toLowerCase().includes(busca.toLowerCase())
  );

  return (
    <div className="mx-auto w-full max-w-6xl space-y-6">
      <section className="rounded-3xl border border-emerald-100 bg-white p-7 shadow-sm">
        <h1 className="text-3xl font-black text-zinc-900">Cobranças e Recebimentos</h1>
        <p className="mt-2 text-zinc-600">
          Gerencie links de pagamento, vencimentos e recuperação de inadimplência com agilidade.
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
          <button className="rounded-xl bg-emerald-500 px-4 py-2.5 text-sm font-semibold text-white hover:bg-emerald-600">
            Nova cobrança
          </button>
        </div>

        <div className="overflow-x-auto rounded-xl border border-zinc-200">
          <table className="min-w-full text-left text-sm">
            <thead className="bg-zinc-100">
              <tr className="text-zinc-700">
                <th className="py-3 px-4">Cliente</th>
                <th className="py-3 px-4">Valor</th>
                <th className="py-3 px-4">Vencimento</th>
                <th className="py-3 px-4">Status</th>
                <th className="py-3 px-4">Ações</th>
              </tr>
            </thead>
            <tbody>
              {filtradas.map((cobranca) => (
                <tr key={cobranca.id} className="border-t border-zinc-200 text-zinc-700">
                  <td className="py-2 px-4">{cobranca.cliente}</td>
                  <td className="py-2 px-4">R$ {cobranca.valor.toFixed(2)}</td>
                  <td className="py-2 px-4">{cobranca.vencimento}</td>
                  <td className="py-2 px-4">
                    <span
                      className={`rounded-full px-2.5 py-1 text-xs font-semibold ${
                        cobranca.status === "Paga" ? "bg-emerald-100 text-emerald-700" : "bg-amber-100 text-amber-700"
                      }`}
                    >
                      {cobranca.status}
                    </span>
                  </td>
                  <td className="py-2 px-4">
                    <a href={cobranca.link} target="_blank" rel="noopener noreferrer" className="mr-3 font-semibold text-cyan-700 hover:text-cyan-800">
                      Ver link
                    </a>
                    <button className="mr-3 font-semibold text-emerald-700 hover:text-emerald-800">Editar</button>
                    <button className="font-semibold text-rose-700 hover:text-rose-800">Excluir</button>
                  </td>
                </tr>
              ))}
              {filtradas.length === 0 && (
                <tr>
                  <td colSpan={5} className="py-4 px-4 text-center text-zinc-500">Nenhuma cobrança encontrada.</td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </section>
    </div>
  );
}
