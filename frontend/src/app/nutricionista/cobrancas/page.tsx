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
  const [cobrancas, setCobrancas] = useState<Cobranca[]>(MOCK_COBRANCAS);
  const [busca, setBusca] = useState("");

  const filtradas = cobrancas.filter(c =>
    c.cliente.toLowerCase().includes(busca.toLowerCase())
  );

  return (
    <div className="min-h-screen bg-gradient-to-br from-emerald-100 via-white to-blue-100 dark:from-zinc-900 dark:via-black dark:to-zinc-800 px-4 py-8">
      <div className="max-w-5xl mx-auto">
        <h1 className="text-3xl font-bold text-emerald-700 dark:text-emerald-300 mb-6">Cobranças</h1>
        <div className="flex gap-4 mb-4">
          <input
            type="text"
            placeholder="Buscar por cliente"
            className="rounded px-4 py-2 border border-zinc-200 dark:border-zinc-700 bg-zinc-50 dark:bg-zinc-800 w-full max-w-xs"
            value={busca}
            onChange={e => setBusca(e.target.value)}
          />
          <button className="rounded bg-emerald-500 hover:bg-emerald-600 text-white px-4 py-2 font-semibold">Nova Cobrança</button>
        </div>
        <div className="overflow-x-auto rounded-xl shadow-lg bg-white dark:bg-zinc-900 border border-emerald-100 dark:border-zinc-800">
          <table className="min-w-full text-left">
            <thead>
              <tr className="bg-emerald-50 dark:bg-zinc-800">
                <th className="py-3 px-4">Cliente</th>
                <th className="py-3 px-4">Valor</th>
                <th className="py-3 px-4">Vencimento</th>
                <th className="py-3 px-4">Status</th>
                <th className="py-3 px-4">Ações</th>
              </tr>
            </thead>
            <tbody>
              {filtradas.map(cobranca => (
                <tr key={cobranca.id} className="border-t border-zinc-100 dark:border-zinc-800">
                  <td className="py-2 px-4">{cobranca.cliente}</td>
                  <td className="py-2 px-4">R$ {cobranca.valor.toFixed(2)}</td>
                  <td className="py-2 px-4">{cobranca.vencimento}</td>
                  <td className="py-2 px-4">{cobranca.status}</td>
                  <td className="py-2 px-4">
                    <a href={cobranca.link} target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:underline mr-2">Ver Link</a>
                    <button className="text-emerald-600 hover:underline mr-2">Editar</button>
                    <button className="text-red-600 hover:underline">Excluir</button>
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
      </div>
    </div>
  );
}
