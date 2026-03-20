"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import React, { useState } from "react";

import { login } from "@/lib/api/auth";

export default function NutriLogin() {
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!email || !password) {
      setError("Preencha todos os campos.");
      return;
    }

    try {
      setLoading(true);
      setError("");
      await login({ email, password });
      router.push("/nutricionista/painel");
      router.refresh();
    } catch (err) {
      const message =
        err instanceof Error ? err.message : "Não foi possível autenticar.";
      setError(message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-gradient-to-br from-emerald-100 via-white to-blue-100 dark:from-zinc-900 dark:via-black dark:to-zinc-800 px-4 py-12">
      <form
        onSubmit={handleSubmit}
        className="bg-white dark:bg-zinc-900 rounded-xl shadow-lg p-8 w-full max-w-md flex flex-col gap-6 border border-blue-100 dark:border-zinc-800"
      >
        <h1 className="text-3xl font-bold text-center text-emerald-700 dark:text-emerald-300 mb-2">
          Login Nutricionista
        </h1>
        <input
          type="email"
          placeholder="E-mail"
          className="rounded px-4 py-3 border border-zinc-200 dark:border-zinc-700 bg-zinc-50 dark:bg-zinc-800 focus:outline-none focus:ring-2 focus:ring-blue-400"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
        />
        <input
          type="password"
          placeholder="Senha"
          className="rounded px-4 py-3 border border-zinc-200 dark:border-zinc-700 bg-zinc-50 dark:bg-zinc-800 focus:outline-none focus:ring-2 focus:ring-blue-400"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
        />
        {error && <div className="text-red-600 text-sm text-center">{error}</div>}
        <button
          disabled={loading}
          type="submit"
          className="rounded-full bg-emerald-500 hover:bg-emerald-600 disabled:opacity-60 text-white px-6 py-3 font-semibold shadow transition-colors"
        >
          {loading ? "Entrando..." : "Entrar"}
        </button>
        <Link
          href="/nutricionista/cadastro"
          className="text-center text-sm text-emerald-700 hover:text-emerald-800"
        >
          Criar conta de nutricionista
        </Link>
      </form>
    </div>
  );
}
