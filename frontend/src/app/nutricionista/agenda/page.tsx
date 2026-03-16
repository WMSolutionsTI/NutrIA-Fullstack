"use client";
import React, { useState } from "react";

interface Consulta {
  id: string;
  cliente: string;
  data: string;
  hora: string;
  status: string;
}

const MOCK_CONSULTAS: Consulta[] = [
  { id: "1", cliente: "Maria Silva", data: "2026-03-15", hora: "09:00", status: "Confirmada" },
  { id: "2", cliente: "João Souza", data: "2026-03-16", hora: "14:30", status: "Pendente" },
];

export default function Agenda() {
  const [consultas, setConsultas] = useState<Consulta[]>(MOCK_CONSULTAS);
  const [busca, setBusca] = useState("");

  const filtradas = consultas.filter(c =>
    c.cliente.toLowerCase().includes(busca.toLowerCase())
  );

  return (
    <div className="min-h-screen bg-gradient-to-br from-emerald-100 via-white to-blue-100 dark:from-zinc-900 dark:via-black dark:to-zinc-800 px-4 py-8">
      <div className="max-w-5xl mx-auto">
        <h1 className="text-3xl font-bold text-emerald-700 dark:text-emerald-300 mb-6">Agenda de Consultas</h1>
        <div className="flex gap-4 mb-4">
          <input
            type="text"
            placeholder="Buscar por cliente"
            className="rounded px-4 py-2 border border-zinc-200 dark:border-zinc-700 bg-zinc-50 dark:bg-zinc-800 w-full max-w-xs"
            value={busca}
            onChange={e => setBusca(e.target.value)}
          />
          <button className="rounded bg-emerald-500 hover:bg-emerald-600 text-white px-4 py-2 font-semibold">Nova Consulta</button>
        </div>
        <div className="overflow-x-auto rounded-xl shadow-lg bg-white dark:bg-zinc-900 border border-emerald-100 dark:border-zinc-800">
          <table className="min-w-full text-left">
            <thead>
              <tr className="bg-emerald-50 dark:bg-zinc-800">
                <th className="py-3 px-4">Cliente</th>
                <th className="py-3 px-4">Data</th>
                <th className="py-3 px-4">Hora</th>
                <th className="py-3 px-4">Status</th>
                <th className="py-3 px-4">Ações</th>
              </tr>
            </thead>
            <tbody>
              {filtradas.map(consulta => (
                <tr key={consulta.id} className="border-t border-zinc-100 dark:border-zinc-800">
                  <td className="py-2 px-4">{consulta.cliente}</td>
                  <td className="py-2 px-4">{consulta.data}</td>
                  <td className="py-2 px-4">{consulta.hora}</td>
                  <td className="py-2 px-4">{consulta.status}</td>
                  <td className="py-2 px-4">
                    <button className="text-blue-600 hover:underline mr-2">Ver</button>
                    <button className="text-emerald-600 hover:underline mr-2">Editar</button>
                    <button className="text-red-600 hover:underline">Cancelar</button>
                  </td>
                </tr>
              ))}
              {filtradas.length === 0 && (
                <tr>
                  <td colSpan={5} className="py-4 px-4 text-center text-zinc-500">Nenhuma consulta encontrada.</td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
