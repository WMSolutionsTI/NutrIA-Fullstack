"use client";

import { useRouter } from "next/navigation";
import React, { useState } from "react";

import { ApiError } from "@/lib/api/client";
import { trocarSenhaPrimeiroAcesso } from "@/lib/api/auth";

export default function PrimeiroAcessoPage() {
  const router = useRouter();
  const [senhaAtual, setSenhaAtual] = useState("");
  const [novaSenha, setNovaSenha] = useState("");
  const [confirmacao, setConfirmacao] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!senhaAtual || !novaSenha || !confirmacao) {
      setError("Preencha todos os campos.");
      return;
    }
    if (novaSenha.length < 8) {
      setError("A nova senha deve ter no mínimo 8 caracteres.");
      return;
    }
    if (novaSenha !== confirmacao) {
      setError("A confirmação da senha não confere.");
      return;
    }

    try {
      setLoading(true);
      setError("");
      await trocarSenhaPrimeiroAcesso({
        senha_atual: senhaAtual,
        nova_senha: novaSenha,
      });
      router.push("/nutricionista/completar-cadastro");
      router.refresh();
    } catch (err) {
      if (err instanceof ApiError) {
        setError(err.detail);
      } else {
        setError("Não foi possível atualizar sua senha.");
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
            Primeiro acesso
          </p>
          <h1 className="mt-5 text-4xl font-black text-zinc-900">Defina sua senha segura</h1>
          <p className="mt-3 text-zinc-600">
            Você entrou com a senha temporária enviada por e-mail. Antes de continuar, crie sua senha definitiva.
          </p>
        </section>

        <form onSubmit={handleSubmit} className="rounded-3xl border border-zinc-200 bg-white p-8 shadow-sm">
          <h2 className="text-2xl font-bold text-zinc-900">Trocar senha</h2>
          <div className="mt-5 space-y-4">
            <input
              type="password"
              placeholder="Senha temporária"
              value={senhaAtual}
              onChange={(e) => setSenhaAtual(e.target.value)}
              className="w-full rounded-xl border border-zinc-200 bg-zinc-50 px-4 py-3"
            />
            <input
              type="password"
              placeholder="Nova senha"
              value={novaSenha}
              onChange={(e) => setNovaSenha(e.target.value)}
              className="w-full rounded-xl border border-zinc-200 bg-zinc-50 px-4 py-3"
            />
            <input
              type="password"
              placeholder="Confirmar nova senha"
              value={confirmacao}
              onChange={(e) => setConfirmacao(e.target.value)}
              className="w-full rounded-xl border border-zinc-200 bg-zinc-50 px-4 py-3"
            />
          </div>
          {error && <div className="mt-4 rounded-lg border border-red-200 bg-red-50 p-3 text-sm text-red-700">{error}</div>}
          <button
            disabled={loading}
            type="submit"
            className="mt-5 w-full rounded-xl bg-emerald-600 px-6 py-3 font-semibold text-white hover:bg-emerald-700 disabled:opacity-60"
          >
            {loading ? "Salvando..." : "Salvar senha e continuar"}
          </button>
        </form>
      </div>
    </div>
  );
}
