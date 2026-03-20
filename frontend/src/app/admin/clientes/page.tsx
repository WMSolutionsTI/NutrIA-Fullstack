"use client";
import React, { useState } from "react";

export default function GestaoClientes() {
  // Simulação de dados
  const [clientes, setClientes] = useState([
    { nome: "João Oliveira", email: "joao@cliente.com", nutricionista: "Ana Silva", status: "Ativo" },
    { nome: "Maria Lima", email: "maria@cliente.com", nutricionista: "Carlos Souza", status: "Inativo" },
  ]);
  const [filtro, setFiltro] = useState("");

  // Filtragem
  const clientesFiltrados = filtro ? clientes.filter(c => c.nome.toLowerCase().includes(filtro.toLowerCase())) : clientes;

  // Simulação de exportação
  const exportar = () => {
    alert("Exportação de clientes simulada!");
  };

  // Simulação de automação IA
  const automacaoIA = "IA ativa: envia follow-ups, engaja clientes, monitora status e sugere ações.";

  return (
    <div className="min-h-screen bg-gradient-to-br from-emerald-100 via-white to-blue-100 dark:from-zinc-900 dark:via-black dark:to-zinc-800 px-4 py-8">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-3xl font-bold text-emerald-700 dark:text-emerald-300 mb-8">Gestão de Clientes</h1>
        {/* Filtros */}
        <section className="mb-6">
          <h2 className="text-xl font-semibold mb-2">Filtrar Clientes</h2>
          <div className="flex gap-4">
            <input value={filtro} onChange={e => setFiltro(e.target.value)} placeholder="Nome do cliente" className="input" />
            <button onClick={exportar} className="rounded bg-blue-600 hover:bg-blue-700 text-white px-6 py-2 font-semibold shadow">Exportar</button>
          </div>
        </section>
        {/* Tabela de clientes */}
        <section className="mb-6">
          <h2 className="text-xl font-semibold mb-2">Lista de Clientes</h2>
          <table className="w-full bg-white dark:bg-zinc-900 rounded shadow">
            <thead>
              <tr>
                <th className="py-2 px-4">Nome</th>
                <th className="py-2 px-4">E-mail</th>
                <th className="py-2 px-4">Nutricionista</th>
                <th className="py-2 px-4">Status</th>
              </tr>
            </thead>
            <tbody>
              {clientesFiltrados.map((c, idx) => (
                <tr key={idx}>
                  <td className="py-2 px-4">{c.nome}</td>
                  <td className="py-2 px-4">{c.email}</td>
                  <td className="py-2 px-4">{c.nutricionista}</td>
                  <td className="py-2 px-4">{c.status}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </section>
        {/* Automação IA */}
        <section className="mb-6">
          <h2 className="text-xl font-semibold mb-2">Automação IA</h2>
          <div className="bg-white dark:bg-zinc-900 rounded p-4 shadow">
            <p>{automacaoIA}</p>
          </div>
        </section>
      </div>
    </div>
  );
}

// Estilos básicos para inputs
// Adicione ao seu CSS global:
// .input { border-radius: 0.5rem; border: 1px solid #d1d5db; padding: 0.5rem; background: #fff; color: #222; }
// .input:focus { outline: none; border-color: #10b981; background: #f0fdf4; }