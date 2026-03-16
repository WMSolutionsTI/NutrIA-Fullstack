"use client";
import React from "react";

// TODO: Buscar dados reais da consulta via API
export default function ConsultaDetalhe({ params }: { params: { id: string } }) {
  // Mock para visualização
  const consulta = {
    id: params.id,
    cliente: "Maria Silva",
    data: "2026-03-15",
    hora: "09:00",
    status: "Confirmada",
    observacoes: "Consulta de retorno."
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-emerald-100 via-white to-blue-100 dark:from-zinc-900 dark:via-black dark:to-zinc-800 px-4 py-8">
      <div className="max-w-3xl mx-auto bg-white dark:bg-zinc-900 rounded-xl shadow-lg p-8 border border-emerald-100 dark:border-zinc-800">
        <h1 className="text-3xl font-bold text-emerald-700 dark:text-emerald-300 mb-4">Consulta de {consulta.cliente}</h1>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
          <div>
            <div className="text-zinc-700 dark:text-zinc-200"><b>Data:</b> {consulta.data}</div>
            <div className="text-zinc-700 dark:text-zinc-200"><b>Hora:</b> {consulta.hora}</div>
            <div className="text-zinc-700 dark:text-zinc-200"><b>Status:</b> {consulta.status}</div>
          </div>
          <div>
            <div className="text-zinc-700 dark:text-zinc-200"><b>Observações:</b> {consulta.observacoes}</div>
          </div>
        </div>
        <div className="flex gap-4 mt-4">
          <button className="rounded bg-emerald-500 hover:bg-emerald-600 text-white px-4 py-2 font-semibold">Editar</button>
          <button className="rounded bg-red-500 hover:bg-red-600 text-white px-4 py-2 font-semibold">Cancelar</button>
        </div>
      </div>
    </div>
  );
}
