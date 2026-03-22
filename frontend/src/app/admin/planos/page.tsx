"use client";

import React, { useState } from "react";

export default function GestaoPlanos() {
  const [planos, setPlanos] = useState([
    { nome: "NutrIA Pro Basic", preco: 99, descricao: "Base operacional para profissionais em crescimento", ativo: true },
    { nome: "NutrIA Pro Premium", preco: 199, descricao: "Suite completa com IA, automações e performance comercial", ativo: true },
  ]);
  const [novoNome, setNovoNome] = useState("");
  const [novoPreco, setNovoPreco] = useState("");
  const [novaDescricao, setNovaDescricao] = useState("");

  const adicionarPlano = () => {
    if (!novoNome || !novoPreco || !novaDescricao) return;
    setPlanos((prev) => [
      ...prev,
      {
        nome: novoNome,
        preco: Number(novoPreco),
        descricao: novaDescricao,
        ativo: true,
      },
    ]);
    setNovoNome("");
    setNovoPreco("");
    setNovaDescricao("");
  };

  const alternarStatus = (idx: number) => {
    setPlanos((prev) => prev.map((p, i) => (i === idx ? { ...p, ativo: !p.ativo } : p)));
  };

  return (
    <div className="space-y-6">
      <section className="rounded-3xl border border-zinc-200 bg-white p-7 shadow-sm">
        <h1 className="text-3xl font-black text-zinc-900">Planos e Assinaturas</h1>
        <p className="mt-2 text-zinc-600">
          Gestão de oferta comercial, precificação e estratégias de monetização.
        </p>
      </section>

      <section className="rounded-2xl border border-zinc-200 bg-white p-6 shadow-sm">
        <h2 className="text-xl font-bold text-zinc-900">Novo plano</h2>
        <div className="mt-4 grid gap-3 md:grid-cols-[1fr_180px_1fr_auto]">
          <input
            value={novoNome}
            onChange={(e) => setNovoNome(e.target.value)}
            placeholder="Nome do plano"
            className="rounded-xl border border-zinc-200 bg-zinc-50 px-4 py-2.5 focus:outline-none focus:ring-2 focus:ring-cyan-300"
          />
          <input
            value={novoPreco}
            onChange={(e) => setNovoPreco(e.target.value)}
            placeholder="Preço"
            type="number"
            className="rounded-xl border border-zinc-200 bg-zinc-50 px-4 py-2.5 focus:outline-none focus:ring-2 focus:ring-cyan-300"
          />
          <input
            value={novaDescricao}
            onChange={(e) => setNovaDescricao(e.target.value)}
            placeholder="Descrição comercial"
            className="rounded-xl border border-zinc-200 bg-zinc-50 px-4 py-2.5 focus:outline-none focus:ring-2 focus:ring-cyan-300"
          />
          <button
            onClick={adicionarPlano}
            className="rounded-xl bg-zinc-900 hover:bg-zinc-800 text-white px-4 py-2.5 text-sm font-semibold"
          >
            Adicionar
          </button>
        </div>
      </section>

      <section className="grid gap-4 md:grid-cols-3">
        <article className="rounded-2xl border border-zinc-200 bg-white p-5 shadow-sm">
          <p className="text-sm text-zinc-500">Planos ativos</p>
          <p className="text-3xl font-black text-zinc-900">{planos.filter((p) => p.ativo).length}</p>
        </article>
        <article className="rounded-2xl border border-zinc-200 bg-white p-5 shadow-sm">
          <p className="text-sm text-zinc-500">Ticket médio estimado</p>
          <p className="text-3xl font-black text-zinc-900">
            R$ {planos.length ? Math.round(planos.reduce((acc, p) => acc + p.preco, 0) / planos.length) : 0}
          </p>
        </article>
        <article className="rounded-2xl border border-zinc-200 bg-white p-5 shadow-sm">
          <p className="text-sm text-zinc-500">Motor de vendas IA</p>
          <p className="mt-1 text-sm font-semibold text-emerald-700">Ativo e integrado ao fluxo comercial</p>
        </article>
      </section>

      <section className="rounded-2xl border border-zinc-200 bg-white p-6 shadow-sm">
        <div className="overflow-x-auto rounded-xl border border-zinc-200">
          <table className="min-w-full text-left">
            <thead className="bg-zinc-100">
              <tr className="text-sm text-zinc-700">
                <th className="px-4 py-3">Plano</th>
                <th className="px-4 py-3">Preço</th>
                <th className="px-4 py-3">Descrição</th>
                <th className="px-4 py-3">Status</th>
                <th className="px-4 py-3">Ações</th>
              </tr>
            </thead>
            <tbody>
              {planos.map((p, idx) => (
                <tr key={`${p.nome}-${idx}`} className="border-t border-zinc-200 text-sm text-zinc-700">
                  <td className="px-4 py-3 font-semibold text-zinc-900">{p.nome}</td>
                  <td className="px-4 py-3">R$ {p.preco}</td>
                  <td className="px-4 py-3">{p.descricao}</td>
                  <td className="px-4 py-3">
                    <span className={`rounded-full px-2.5 py-1 text-xs font-semibold ${p.ativo ? "bg-emerald-100 text-emerald-700" : "bg-zinc-200 text-zinc-700"}`}>
                      {p.ativo ? "Ativo" : "Inativo"}
                    </span>
                  </td>
                  <td className="px-4 py-3">
                    <button
                      onClick={() => alternarStatus(idx)}
                      className="rounded-lg border border-zinc-300 bg-white px-3 py-1.5 text-xs font-semibold hover:bg-zinc-50"
                    >
                      {p.ativo ? "Desativar" : "Ativar"}
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
