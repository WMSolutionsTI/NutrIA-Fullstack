"use client";

import Link from "next/link";
import React, { useEffect, useState } from "react";
import { getClientes, novoCliente } from "@/lib/api";

interface Cliente {
  id: string;
  nome: string;
  email: string;
  telefone: string;
  status: string;
}

const MOCK_CLIENTES: Cliente[] = [
  { id: "1", nome: "Maria Silva", email: "maria@email.com", telefone: "(11) 99999-0001", status: "Ativo" },
  { id: "2", nome: "João Souza", email: "joao@email.com", telefone: "(11) 99999-0002", status: "Inativo" },
];

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
    <div className="mx-auto w-full max-w-6xl space-y-6">
      <section className="rounded-3xl border border-emerald-100 bg-white p-7 shadow-sm">
        <h1 className="text-3xl font-black text-zinc-900">Clientes</h1>
        <p className="mt-2 text-zinc-600">
          Gerencie sua base ativa e acompanhe relacionamento, status e histórico de atendimento.
        </p>
      </section>

      <section className="rounded-2xl border border-zinc-200 bg-white p-6 shadow-sm">
        <div className="mb-4 flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
          <div className="flex w-full flex-wrap gap-3">
            <input
              type="text"
              placeholder="Buscar por nome ou e-mail"
              className="w-full rounded-xl border border-zinc-200 bg-zinc-50 px-4 py-2.5 text-sm md:max-w-sm"
              value={busca}
              onChange={(e) => setBusca(e.target.value)}
            />
          </div>
          <Link href="/nutricionista/clientes/novo" className="rounded-xl bg-emerald-500 px-4 py-2.5 text-sm font-semibold text-white hover:bg-emerald-600">
            Novo cliente
          </Link>
        </div>

        <details className="rounded-xl border border-zinc-200 bg-zinc-50 p-4">
            <summary className="font-semibold cursor-pointer">Cadastrar novo cliente</summary>
            <div className="grid grid-cols-1 md:grid-cols-4 gap-2 mt-3">
              <input
                type="text"
                placeholder="Nome"
                value={novoNome}
                onChange={(e) => setNovoNome(e.target.value)}
                className="rounded-xl border border-zinc-200 bg-white px-3 py-2 text-sm"
              />
              <input
                type="email"
                placeholder="E-mail"
                value={novoEmail}
                onChange={(e) => setNovoEmail(e.target.value)}
                className="rounded-xl border border-zinc-200 bg-white px-3 py-2 text-sm"
              />
              <input
                type="text"
                placeholder="Telefone"
                value={novoTelefone}
                onChange={(e) => setNovoTelefone(e.target.value)}
                className="rounded-xl border border-zinc-200 bg-white px-3 py-2 text-sm"
              />
              <select
                value={novoStatus}
                onChange={(e) => setNovoStatus(e.target.value)}
                className="rounded-xl border border-zinc-200 bg-white px-3 py-2 text-sm"
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
                    setClientes(
                      (prev) =>
                        [
                          ...prev,
                          { id: String(created.id), nome: novoNome, email: novoEmail, telefone: novoTelefone, status: novoStatus },
                        ] as Cliente[]
                    );
                    setNovoNome("");
                    setNovoEmail("");
                    setNovoTelefone("");
                    setNovoStatus("cliente_potencial");
                  } catch (error) {
                    console.error(error);
                    setErro("Erro ao criar cliente");
                  }
                }}
                className="rounded-xl bg-emerald-500 px-4 py-2 text-sm font-semibold text-white hover:bg-emerald-600"
              >
                Criar
              </button>
              {erro && <span className="text-sm font-semibold text-rose-700">{erro}</span>}
            </div>
        </details>

        <div className="overflow-x-auto rounded-xl border border-zinc-200">
          <table className="min-w-full text-left text-sm">
            <thead className="bg-zinc-100">
              <tr className="text-zinc-700">
                <th className="py-3 px-4">Nome</th>
                <th className="py-3 px-4">E-mail</th>
                <th className="py-3 px-4">Telefone</th>
                <th className="py-3 px-4">Status</th>
                <th className="py-3 px-4">Ações</th>
              </tr>
            </thead>
            <tbody>
              {filtrados.map((cliente) => (
                <tr key={cliente.id} className="border-t border-zinc-200 text-zinc-700">
                  <td className="py-2 px-4 font-semibold text-zinc-900">{cliente.nome}</td>
                  <td className="py-2 px-4">{cliente.email}</td>
                  <td className="py-2 px-4">{cliente.telefone}</td>
                  <td className="py-2 px-4">
                    <span className="rounded-full bg-zinc-200 px-2.5 py-1 text-xs font-semibold text-zinc-700">{cliente.status}</span>
                  </td>
                  <td className="py-2 px-4">
                    <Link className="mr-3 font-semibold text-cyan-700 hover:text-cyan-800" href={`/nutricionista/clientes/${cliente.id}`}>
                      Ver
                    </Link>
                    <button className="mr-3 font-semibold text-emerald-700 hover:text-emerald-800">Editar</button>
                    <button className="font-semibold text-rose-700 hover:text-rose-800">Excluir</button>
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
      </section>
    </div>
  );
}
