"use client";
import React, { useState } from "react";

interface Cliente {
  id: string;
  nome: string;
  email: string;
  telefone: string;
  status: string;
}

// Mock inicial para visual
const MOCK_CLIENTES: Cliente[] = [
  { id: "1", nome: "Maria Silva", email: "maria@email.com", telefone: "(11) 99999-0001", status: "Ativo" },
  { id: "2", nome: "João Souza", email: "joao@email.com", telefone: "(11) 99999-0002", status: "Inativo" },
];

import { useEffect } from "react";
import { getClientes, novoCliente } from "@/lib/api";

export default function Clientes() {
  const [clientes, setClientes] = useState<Cliente[]>(MOCK_CLIENTES);
  const [busca, setBusca] = useState("");
  const [novoNome, setNovoNome] = useState("");
  const [novoEmail, setNovoEmail] = useState("");
  const [novoTelefone, setNovoTelefone] = useState("");
  const [novoStatus, setNovoStatus] = useState("cliente_potencial");
  const [erro, setErro] = useState("");

  useEffect(() => {
    async function loadClientes() {
      try {
        const data = await getClientes();
        setClientes(Array.isArray(data) && data.length ? data : MOCK_CLIENTES);
      } catch (e) {
        console.error("Falha ao buscar clientes", e);
      }
    }
    loadClientes();
  }, []);

  const filtrados = clientes.filter(c =>
    c.nome.toLowerCase().includes(busca.toLowerCase()) ||
    c.email.toLowerCase().includes(busca.toLowerCase())
  );

  return (
    <div className="min-h-screen bg-gradient-to-br from-emerald-100 via-white to-blue-100 dark:from-zinc-900 dark:via-black dark:to-zinc-800 px-4 py-8">
      <div className="max-w-5xl mx-auto">
        <h1 className="text-3xl font-bold text-emerald-700 dark:text-emerald-300 mb-6">Clientes</h1>
        <div className="flex flex-col gap-4 mb-4">
          <div className="flex flex-wrap gap-3">
            <input
              type="text"
              placeholder="Buscar por nome ou e-mail"
              className="rounded px-4 py-2 border border-zinc-200 dark:border-zinc-700 bg-zinc-50 dark:bg-zinc-800 w-full max-w-xs"
              value={busca}
              onChange={e => setBusca(e.target.value)}
            />
          </div>

          <details className="bg-zinc-100 dark:bg-zinc-800 p-3 rounded-md border border-zinc-200 dark:border-zinc-700">
            <summary className="font-semibold cursor-pointer">Cadastrar novo cliente</summary>
            <div className="grid grid-cols-1 md:grid-cols-4 gap-2 mt-3">
              <input
                type="text"
                placeholder="Nome"
                value={novoNome}
                onChange={e => setNovoNome(e.target.value)}
                className="rounded px-3 py-2 border border-zinc-300 dark:border-zinc-700 bg-white dark:bg-zinc-900"
              />
              <input
                type="email"
                placeholder="E-mail"
                value={novoEmail}
                onChange={e => setNovoEmail(e.target.value)}
                className="rounded px-3 py-2 border border-zinc-300 dark:border-zinc-700 bg-white dark:bg-zinc-900"
              />
              <input
                type="text"
                placeholder="Telefone"
                value={novoTelefone}
                onChange={e => setNovoTelefone(e.target.value)}
                className="rounded px-3 py-2 border border-zinc-300 dark:border-zinc-700 bg-white dark:bg-zinc-900"
              />
              <select
                value={novoStatus}
                onChange={e => setNovoStatus(e.target.value)}
                className="rounded px-3 py-2 border border-zinc-300 dark:border-zinc-700 bg-white dark:bg-zinc-900"
              >
                <option value="cliente_potencial">Potencial</option>
                <option value="cliente_ativo">Ativo</option>
                <option value="cliente_inativo">Inativo</option>
                <option value="cliente_satisfeito">Satisfeito</option>
              </select>
            </div>
            <div className="mt-3 flex gap-2">
              <button
                onClick={async () => {
                  if (!novoNome || !novoEmail || !novoTelefone) {
                    setErro("Preencha nome, e-mail e telefone");
                    return;
                  }
                  setErro("");
                  try {
                    const created = await novoCliente({
                      nome: novoNome,
                      email: novoEmail,
                      contato_chatwoot: novoTelefone,
                      status: novoStatus,
                      nutricionista_id: 1,
                    });
                    setClientes(prev => [...prev, { id: String(created.id), nome: novoNome, email: novoEmail, telefone: novoTelefone, status: novoStatus }] as Cliente[]);
                    setNovoNome("");
                    setNovoEmail("");
                    setNovoTelefone("");
                    setNovoStatus("cliente_potencial");
                  } catch (error) {
                    console.error(error);
                    setErro("Erro ao criar cliente");
                  }
                }}
                className="rounded bg-emerald-500 hover:bg-emerald-600 text-white px-4 py-2 font-semibold"
              >
                Criar
              </button>
              {erro && <span className="text-sm text-red-600">{erro}</span>}
            </div>
          </details>
        </div>
        <div className="overflow-x-auto rounded-xl shadow-lg bg-white dark:bg-zinc-900 border border-emerald-100 dark:border-zinc-800">
          <table className="min-w-full text-left">
            <thead>
              <tr className="bg-emerald-50 dark:bg-zinc-800">
                <th className="py-3 px-4">Nome</th>
                <th className="py-3 px-4">E-mail</th>
                <th className="py-3 px-4">Telefone</th>
                <th className="py-3 px-4">Status</th>
                <th className="py-3 px-4">Ações</th>
              </tr>
            </thead>
            <tbody>
              {filtrados.map(cliente => (
                <tr key={cliente.id} className="border-t border-zinc-100 dark:border-zinc-800">
                  <td className="py-2 px-4">{cliente.nome}</td>
                  <td className="py-2 px-4">{cliente.email}</td>
                  <td className="py-2 px-4">{cliente.telefone}</td>
                  <td className="py-2 px-4">{cliente.status}</td>
                  <td className="py-2 px-4">
                    <button className="text-blue-600 hover:underline mr-2">Ver</button>
                    <button className="text-emerald-600 hover:underline mr-2">Editar</button>
                    <button className="text-red-600 hover:underline">Excluir</button>
                  </td>
                </tr>
              ))}
              {filtrados.length === 0 && (
                <tr>
                  <td colSpan={5} className="py-4 px-4 text-center text-zinc-500">Nenhum cliente encontrado.</td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
