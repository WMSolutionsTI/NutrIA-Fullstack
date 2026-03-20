"use client";
import React, { useState } from "react";

export default function GestaoNutricionistas() {
  // Simulação de dados
  const [nutricionistas, setNutricionistas] = useState([
    { nome: "Ana Silva", email: "ana@nutria.com", ativo: true },
    { nome: "Carlos Souza", email: "carlos@nutria.com", ativo: false },
  ]);
  const [novoNome, setNovoNome] = useState("");
  const [novoEmail, setNovoEmail] = useState("");

  const adicionarNutricionista = () => {
    if (novoNome && novoEmail) {
      setNutricionistas([...nutricionistas, { nome: novoNome, email: novoEmail, ativo: true }]);
      setNovoNome("");
      setNovoEmail("");
    }
  };

  const alternarStatus = (idx: number) => {
    setNutricionistas(nutricionistas.map((n, i) => i === idx ? { ...n, ativo: !n.ativo } : n));
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-100 via-white to-emerald-100 dark:from-zinc-900 dark:via-black dark:to-zinc-800 px-4 py-8">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-3xl font-bold text-blue-700 dark:text-blue-300 mb-8">Gestão de Nutricionistas</h1>
        {/* Cadastro */}
        <section className="mb-6">
          <h2 className="text-xl font-semibold mb-2">Cadastrar Nutricionista</h2>
          <div className="flex gap-4">
            <input value={novoNome} onChange={e => setNovoNome(e.target.value)} placeholder="Nome" className="input" />
            <input value={novoEmail} onChange={e => setNovoEmail(e.target.value)} placeholder="E-mail" className="input" />
            <button onClick={adicionarNutricionista} className="rounded bg-blue-600 hover:bg-blue-700 text-white px-6 py-2 font-semibold shadow">Adicionar</button>
          </div>
        </section>
        {/* Tabela de nutricionistas */}
        <section className="mb-6">
          <h2 className="text-xl font-semibold mb-2">Lista de Nutricionistas</h2>
          <table className="w-full bg-white dark:bg-zinc-900 rounded shadow">
            <thead>
              <tr>
                <th className="py-2 px-4">Nome</th>
                <th className="py-2 px-4">E-mail</th>
                <th className="py-2 px-4">Status</th>
                <th className="py-2 px-4">Ações</th>
              </tr>
            </thead>
            <tbody>
              {nutricionistas.map((n, idx) => (
                <tr key={idx}>
                  <td className="py-2 px-4">{n.nome}</td>
                  <td className="py-2 px-4">{n.email}</td>
                  <td className="py-2 px-4">{n.ativo ? "Ativo" : "Inativo"}</td>
                  <td className="py-2 px-4">
                    <button onClick={() => alternarStatus(idx)} className="rounded bg-emerald-500 hover:bg-emerald-600 text-white px-4 py-1 font-semibold shadow">
                      {n.ativo ? "Desativar" : "Ativar"}
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </section>
      </div>
    </div>
  );
}

// Estilos básicos para inputs
// Adicione ao seu CSS global:
// .input { border-radius: 0.5rem; border: 1px solid #d1d5db; padding: 0.5rem; background: #fff; color: #222; }
// .input:focus { outline: none; border-color: #3b82f6; background: #f0f6ff; }