"use client";

import React, { useState } from "react";

export default function GestaoNutricionistas() {
  const [nutricionistas, setNutricionistas] = useState([
    { nome: "Ana Silva", email: "ana@nutria.com", ativo: true },
    { nome: "Carlos Souza", email: "carlos@nutria.com", ativo: false },
  ]);
  const [novoNome, setNovoNome] = useState("");
  const [novoEmail, setNovoEmail] = useState("");

  const adicionarNutricionista = () => {
    if (!novoNome || !novoEmail) return;
    setNutricionistas((prev) => [...prev, { nome: novoNome, email: novoEmail, ativo: true }]);
    setNovoNome("");
    setNovoEmail("");
  };

  const alternarStatus = (idx: number) => {
    setNutricionistas((prev) => prev.map((n, i) => (i === idx ? { ...n, ativo: !n.ativo } : n)));
  };

  return (
    <div className="space-y-6">
      <section className="rounded-3xl border border-zinc-200 bg-white p-7 shadow-sm">
        <h1 className="text-3xl font-black text-zinc-900">Gestão de Nutricionistas</h1>
        <p className="mt-2 text-zinc-600">Onboarding, ativação e governança de contas profissionais da plataforma.</p>
      </section>

      <section className="rounded-2xl border border-zinc-200 bg-white p-6 shadow-sm">
        <h2 className="text-xl font-bold text-zinc-900">Cadastrar nutricionista</h2>
        <div className="mt-4 grid gap-3 md:grid-cols-[1fr_1fr_auto]">
          <input
            value={novoNome}
            onChange={(e) => setNovoNome(e.target.value)}
            placeholder="Nome"
            className="rounded-xl border border-zinc-200 bg-zinc-50 px-4 py-2.5 focus:outline-none focus:ring-2 focus:ring-cyan-300"
          />
          <input
            value={novoEmail}
            onChange={(e) => setNovoEmail(e.target.value)}
            placeholder="E-mail"
            className="rounded-xl border border-zinc-200 bg-zinc-50 px-4 py-2.5 focus:outline-none focus:ring-2 focus:ring-cyan-300"
          />
          <button
            onClick={adicionarNutricionista}
            className="rounded-xl bg-zinc-900 hover:bg-zinc-800 text-white px-4 py-2.5 text-sm font-semibold"
          >
            Adicionar
          </button>
        </div>
      </section>

      <section className="rounded-2xl border border-zinc-200 bg-white p-6 shadow-sm">
        <h2 className="text-xl font-bold text-zinc-900">Contas cadastradas</h2>
        <div className="mt-4 overflow-x-auto rounded-xl border border-zinc-200">
          <table className="min-w-full text-left">
            <thead className="bg-zinc-100">
              <tr className="text-sm text-zinc-700">
                <th className="px-4 py-3">Nome</th>
                <th className="px-4 py-3">E-mail</th>
                <th className="px-4 py-3">Status</th>
                <th className="px-4 py-3">Ações</th>
              </tr>
            </thead>
            <tbody>
              {nutricionistas.map((n, idx) => (
                <tr key={`${n.email}-${idx}`} className="border-t border-zinc-200 text-sm text-zinc-700">
                  <td className="px-4 py-3 font-semibold text-zinc-900">{n.nome}</td>
                  <td className="px-4 py-3">{n.email}</td>
                  <td className="px-4 py-3">
                    <span className={`rounded-full px-2.5 py-1 text-xs font-semibold ${n.ativo ? "bg-emerald-100 text-emerald-700" : "bg-zinc-200 text-zinc-700"}`}>
                      {n.ativo ? "Ativo" : "Inativo"}
                    </span>
                  </td>
                  <td className="px-4 py-3">
                    <button
                      onClick={() => alternarStatus(idx)}
                      className="rounded-lg border border-zinc-300 bg-white px-3 py-1.5 text-xs font-semibold hover:bg-zinc-50"
                    >
                      {n.ativo ? "Desativar" : "Ativar"}
                    </button>
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
