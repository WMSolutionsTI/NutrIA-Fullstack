"use client";

import { useRouter } from "next/navigation";
import React, { useState } from "react";

import { ApiError } from "@/lib/api/client";
import { completarPerfilPessoal } from "@/lib/api/auth";

export default function CompletarCadastroPage() {
  const router = useRouter();
  const [cpf, setCpf] = useState("");
  const [cnpj, setCnpj] = useState("");
  const [endereco, setEndereco] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!cpf || !endereco) {
      setError("CPF e endereço são obrigatórios.");
      return;
    }

    try {
      setLoading(true);
      setError("");
      await completarPerfilPessoal({ cpf, cnpj, endereco });
      router.push("/nutricionista/painel?setup=pendente");
      router.refresh();
    } catch (err) {
      if (err instanceof ApiError) {
        setError(err.detail);
      } else {
        setError("Não foi possível concluir seu cadastro.");
      }
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="min-h-screen bg-[radial-gradient(circle_at_12%_14%,#86efac30,transparent_36%),radial-gradient(circle_at_85%_0%,#67e8f930,transparent_45%),linear-gradient(145deg,#f6fff7_0%,#eef8ff_65%,#f5fff9_100%)] px-4 py-12">
      <div className="mx-auto grid w-full max-w-5xl gap-8 lg:grid-cols-[1.1fr_0.9fr]">
        <section className="rounded-3xl border border-emerald-100 bg-white p-8 shadow-sm">
          <p className="inline-flex rounded-full border border-emerald-200 bg-emerald-50 px-4 py-1 text-sm font-semibold text-emerald-700">
            Cadastro obrigatório
          </p>
          <h1 className="mt-5 text-4xl font-black text-zinc-900">Complete seus dados pessoais</h1>
          <p className="mt-3 text-zinc-600">
            Para liberar seu painel e concluir o onboarding da secretária, finalize seu cadastro com os dados fiscais e endereço.
          </p>
        </section>

        <form onSubmit={handleSubmit} className="rounded-3xl border border-zinc-200 bg-white p-8 shadow-sm">
          <h2 className="text-2xl font-bold text-zinc-900">Dados pessoais</h2>
          <div className="mt-5 space-y-4">
            <input
              type="text"
              placeholder="CPF (obrigatório)"
              value={cpf}
              onChange={(e) => setCpf(e.target.value)}
              className="w-full rounded-xl border border-zinc-200 bg-zinc-50 px-4 py-3"
            />
            <input
              type="text"
              placeholder="CNPJ (se houver)"
              value={cnpj}
              onChange={(e) => setCnpj(e.target.value)}
              className="w-full rounded-xl border border-zinc-200 bg-zinc-50 px-4 py-3"
            />
            <input
              type="text"
              placeholder="Endereço completo"
              value={endereco}
              onChange={(e) => setEndereco(e.target.value)}
              className="w-full rounded-xl border border-zinc-200 bg-zinc-50 px-4 py-3"
            />
          </div>
          {error && <div className="mt-4 rounded-lg border border-red-200 bg-red-50 p-3 text-sm text-red-700">{error}</div>}
          <button
            disabled={loading}
            type="submit"
            className="mt-5 w-full rounded-xl bg-emerald-600 px-6 py-3 font-semibold text-white hover:bg-emerald-700 disabled:opacity-60"
          >
            {loading ? "Salvando..." : "Salvar e ir para o dashboard"}
          </button>
        </form>
      </div>
    </div>
  );
}
