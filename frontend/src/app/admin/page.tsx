"use client";
import React, { useState } from "react";

export default function AdminLogin() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    // TODO: Implementar autenticação real
    if (!email || !password) {
      setError("Preencha todos os campos.");
      return;
    }
    setError("");
    alert("Login de admin simulado!");
  };

  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-gradient-to-br from-blue-100 via-white to-emerald-100 dark:from-zinc-900 dark:via-black dark:to-zinc-800 px-4 py-12">
      <form onSubmit={handleSubmit} className="bg-white dark:bg-zinc-900 rounded-xl shadow-lg p-8 w-full max-w-md flex flex-col gap-6 border border-emerald-100 dark:border-zinc-800">
        <h1 className="text-3xl font-bold text-center text-blue-700 dark:text-emerald-300 mb-2">Login Admin</h1>
        <input
          type="email"
          placeholder="E-mail"
          className="rounded px-4 py-3 border border-zinc-200 dark:border-zinc-700 bg-zinc-50 dark:bg-zinc-800 focus:outline-none focus:ring-2 focus:ring-emerald-400"
          value={email}
          onChange={e => setEmail(e.target.value)}
        />
        <input
          type="password"
          placeholder="Senha"
          className="rounded px-4 py-3 border border-zinc-200 dark:border-zinc-700 bg-zinc-50 dark:bg-zinc-800 focus:outline-none focus:ring-2 focus:ring-emerald-400"
          value={password}
          onChange={e => setPassword(e.target.value)}
        />
        {error && <div className="text-red-600 text-sm text-center">{error}</div>}
        <button type="submit" className="rounded-full bg-blue-600 hover:bg-blue-700 text-white px-6 py-3 font-semibold shadow transition-colors">Entrar</button>
      </form>
    </div>
  );
}
