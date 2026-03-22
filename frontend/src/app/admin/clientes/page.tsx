"use client";

import React, { useMemo, useState } from "react";

export default function GestaoClientes() {
  const [clientes] = useState([
    { nome: "João Oliveira", email: "joao@cliente.com", nutricionista: "Ana Silva", status: "Ativo" },
    { nome: "Maria Lima", email: "maria@cliente.com", nutricionista: "Carlos Souza", status: "Inativo" },
    { nome: "Fernanda Rocha", email: "fernanda@cliente.com", nutricionista: "Ana Silva", status: "Ativo" },
  ]);
  const [filtro, setFiltro] = useState("");

  const clientesFiltrados = useMemo(
    () =>
      filtro
        ? clientes.filter((c) => c.nome.toLowerCase().includes(filtro.toLowerCase()))
        : clientes,
    [clientes, filtro]
  );

  return (
    <div className="space-y-6">
      <section className="rounded-3xl border border-zinc-200 bg-white p-7 shadow-sm">
        <h1 className="text-3xl font-black text-zinc-900">Gestão de Clientes</h1>
        <p className="mt-2 text-zinc-600">
          Controle de base ativa, relacionamento e qualidade de atendimento por nutricionista.
        </p>
      </section>

      <section className="rounded-2xl border border-zinc-200 bg-white p-6 shadow-sm">
        <div className="flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
          <input
            value={filtro}
            onChange={(e) => setFiltro(e.target.value)}
            placeholder="Buscar por nome"
            className="w-full md:max-w-xs rounded-xl border border-zinc-200 bg-zinc-50 px-4 py-2.5 focus:outline-none focus:ring-2 focus:ring-cyan-300"
          />
          <button className="rounded-xl bg-zinc-900 hover:bg-zinc-800 text-white px-4 py-2.5 text-sm font-semibold">
            Exportar relatório
          </button>
        </div>

        <div className="mt-5 overflow-x-auto rounded-xl border border-zinc-200">
          <table className="min-w-full text-left">
            <thead className="bg-zinc-100">
              <tr className="text-sm text-zinc-700">
                <th className="px-4 py-3">Nome</th>
                <th className="px-4 py-3">E-mail</th>
                <th className="px-4 py-3">Nutricionista</th>
                <th className="px-4 py-3">Status</th>
              </tr>
            </thead>
            <tbody>
              {clientesFiltrados.map((c) => (
                <tr key={`${c.email}-${c.nome}`} className="border-t border-zinc-200 text-sm text-zinc-700">
                  <td className="px-4 py-3 font-semibold text-zinc-900">{c.nome}</td>
                  <td className="px-4 py-3">{c.email}</td>
                  <td className="px-4 py-3">{c.nutricionista}</td>
                  <td className="px-4 py-3">
                    <span
                      className={`rounded-full px-2.5 py-1 text-xs font-semibold ${
                        c.status === "Ativo" ? "bg-emerald-100 text-emerald-700" : "bg-zinc-200 text-zinc-700"
                      }`}
                    >
                      {c.status}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>
    </div>
  );
}
