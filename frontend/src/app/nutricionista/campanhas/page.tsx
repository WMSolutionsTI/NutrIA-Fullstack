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
  const [campanhas, setCampanhas] = useState<Campanha[]>(MOCK_CAMPANHAS);
  const [busca, setBusca] = useState("");

  const filtradas = campanhas.filter(c =>
    c.titulo.toLowerCase().includes(busca.toLowerCase())
  );

  return (
    <div className="min-h-screen bg-gradient-to-br from-emerald-100 via-white to-blue-100 dark:from-zinc-900 dark:via-black dark:to-zinc-800 px-4 py-8">
      <div className="max-w-5xl mx-auto">
        <h1 className="text-3xl font-bold text-emerald-700 dark:text-emerald-300 mb-6">Campanhas</h1>
        <div className="flex gap-4 mb-4">
          <input
            type="text"
            placeholder="Buscar por título"
            className="rounded px-4 py-2 border border-zinc-200 dark:border-zinc-700 bg-zinc-50 dark:bg-zinc-800 w-full max-w-xs"
            value={busca}
            onChange={e => setBusca(e.target.value)}
          />
          <button className="rounded bg-emerald-500 hover:bg-emerald-600 text-white px-4 py-2 font-semibold">Nova Campanha</button>
        </div>
        <div className="overflow-x-auto rounded-xl shadow-lg bg-white dark:bg-zinc-900 border border-emerald-100 dark:border-zinc-800">
          <table className="min-w-full text-left">
            <thead>
              <tr className="bg-emerald-50 dark:bg-zinc-800">
                <th className="py-3 px-4">Título</th>
                <th className="py-3 px-4">Mensagem</th>
                <th className="py-3 px-4">Data</th>
                <th className="py-3 px-4">Status</th>
                <th className="py-3 px-4">Ações</th>
              </tr>
            </thead>
            <tbody>
              {filtradas.map(campanha => (
                <tr key={campanha.id} className="border-t border-zinc-100 dark:border-zinc-800">
                  <td className="py-2 px-4">{campanha.titulo}</td>
                  <td className="py-2 px-4">{campanha.mensagem}</td>
                  <td className="py-2 px-4">{campanha.data}</td>
                  <td className="py-2 px-4">{campanha.status}</td>
                  <td className="py-2 px-4">
                    <button className="text-blue-600 hover:underline mr-2">Ver</button>
                    <button className="text-emerald-600 hover:underline mr-2">Editar</button>
                    <button className="text-red-600 hover:underline">Excluir</button>
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
      </div>
    </div>
  );
}
