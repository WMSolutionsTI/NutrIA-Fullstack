"use client";
import React from "react";

// TODO: Buscar dados reais do cliente via API
export default function ClienteDetalhe({ params }: { params: { id: string } }) {
  // Mock para visualização
  const cliente = {
    id: params.id,
    nome: "Maria Silva",
    email: "maria@email.com",
    telefone: "(11) 99999-0001",
    nascimento: "1990-01-01",
    status: "Ativo",
    observacoes: "Paciente com restrição a lactose."
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-emerald-100 via-white to-blue-100 dark:from-zinc-900 dark:via-black dark:to-zinc-800 px-4 py-8">
      <div className="max-w-3xl mx-auto bg-white dark:bg-zinc-900 rounded-xl shadow-lg p-8 border border-emerald-100 dark:border-zinc-800">
        <h1 className="text-3xl font-bold text-emerald-700 dark:text-emerald-300 mb-4">{cliente.nome}</h1>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
          <div>
            <div className="text-zinc-700 dark:text-zinc-200"><b>E-mail:</b> {cliente.email}</div>
            <div className="text-zinc-700 dark:text-zinc-200"><b>Telefone:</b> {cliente.telefone}</div>
            <div className="text-zinc-700 dark:text-zinc-200"><b>Nascimento:</b> {cliente.nascimento}</div>
            <div className="text-zinc-700 dark:text-zinc-200"><b>Status:</b> {cliente.status}</div>
          </div>
          <div>
            <div className="text-zinc-700 dark:text-zinc-200"><b>Observações:</b> {cliente.observacoes}</div>
          </div>
        </div>
        <div className="flex gap-4 mt-4">
          <button className="rounded bg-emerald-500 hover:bg-emerald-600 text-white px-4 py-2 font-semibold">Editar</button>
          <button className="rounded bg-red-500 hover:bg-red-600 text-white px-4 py-2 font-semibold">Excluir</button>
        </div>
      </div>
    </div>
  );
}
