"use client";

import React, { useState } from "react";

export default function GestaoPlanos() {
  // Simulação de dados
  const [planos, setPlanos] = useState([
    { nome: "NutrIA Pro Basic", preco: 99, descricao: "Plano básico para nutricionistas iniciantes", ativo: true },
    { nome: "NutrIA Pro Premium", preco: 199, descricao: "Plano avançado com IA, automações e integrações", ativo: true },
  ]);
  const [novoNome, setNovoNome] = useState("");
  const [novoPreco, setNovoPreco] = useState("");
  const [novaDescricao, setNovaDescricao] = useState("");

  const adicionarPlano = () => {
    if (novoNome && novoPreco && novaDescricao) {
      setPlanos([...planos, { nome: novoNome, preco: parseFloat(novoPreco), descricao: novaDescricao, ativo: true }]);
      setNovoNome("");
      setNovoPreco("");
      setNovaDescricao("");
    }
  };

  const alternarStatus = (idx: number) => {
    setPlanos(planos.map((p, i) => i === idx ? { ...p, ativo: !p.ativo } : p));
  };

  // Simulação de vendas automatizadas por IA
  const vendasIA = 32;
  const conversao = 18;

  return (
    <div className="min-h-screen bg-gradient-to-br from-yellow-100 via-white to-blue-100 dark:from-zinc-900 dark:via-black dark:to-zinc-800 px-4 py-8">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-3xl font-bold text-yellow-700 dark:text-yellow-300 mb-8">Gestão de Planos e Assinaturas</h1>
        {/* Cadastro */}
        <section className="mb-6">
          <h2 className="text-xl font-semibold mb-2">Cadastrar Plano</h2>
          <div className="flex gap-4">
            <input value={novoNome} onChange={e => setNovoNome(e.target.value)} placeholder="Nome do plano" className="input" />
            <input value={novoPreco} onChange={e => setNovoPreco(e.target.value)} placeholder="Preço (R$)" className="input" type="number" />
            <input value={novaDescricao} onChange={e => setNovaDescricao(e.target.value)} placeholder="Descrição" className="input" />
            <button onClick={adicionarPlano} className="rounded bg-yellow-600 hover:bg-yellow-700 text-white px-6 py-2 font-semibold shadow">Adicionar</button>
          </div>
        </section>
        {/* Tabela de planos */}
        <section className="mb-6">
          <h2 className="text-xl font-semibold mb-2">Lista de Planos</h2>
          <table className="w-full bg-white dark:bg-zinc-900 rounded shadow">
            <thead>
              <tr>
                <th className="py-2 px-4">Nome</th>
                <th className="py-2 px-4">Preço</th>
                <th className="py-2 px-4">Descrição</th>
                <th className="py-2 px-4">Status</th>
                <th className="py-2 px-4">Ações</th>
              </tr>
            </thead>
            <tbody>
              {planos.map((p, idx) => (
                <tr key={idx}>
                  <td className="py-2 px-4">{p.nome}</td>
                  <td className="py-2 px-4">R$ {p.preco}</td>
                  <td className="py-2 px-4">{p.descricao}</td>
                  <td className="py-2 px-4">{p.ativo ? "Ativo" : "Inativo"}</td>
                  <td className="py-2 px-4">
                    <button onClick={() => alternarStatus(idx)} className="rounded bg-blue-600 hover:bg-blue-700 text-white px-4 py-1 font-semibold shadow">
                      {p.ativo ? "Desativar" : "Ativar"}
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </section>
        {/* Vendas automatizadas por IA e métricas */}
        <section className="mb-6">
          <h2 className="text-xl font-semibold mb-2">Vendas Automatizadas por IA</h2>
          <div className="bg-white dark:bg-zinc-900 rounded p-4 shadow">
            <p>Vendas realizadas por agentes IA: <span className="font-bold">{vendasIA}</span></p>
            <p>Taxa de conversão: <span className="font-bold">{conversao}%</span></p>
            <p>Integração Assas: <span className="font-bold">Ativa</span></p>
          </div>
        </section>
      </div>
    </div>
  );
}

// Estilos básicos para inputs
// Adicione ao seu CSS global:
// .input { border-radius: 0.5rem; border: 1px solid #d1d5db; padding: 0.5rem; background: #fff; color: #222; }
// .input:focus { outline: none; border-color: #f59e42; background: #fff7ed; }