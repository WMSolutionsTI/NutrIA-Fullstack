"use client";
import React from "react";
import Link from "next/link";
import { useUser } from "@/context/UserContext";

export default function NutriNavbar() {
  const { logout } = useUser();

  return (
    <header className="w-full flex justify-between items-center px-6 py-4 bg-white/80 dark:bg-zinc-900/80 shadow-sm sticky top-0 z-30">
      <div className="flex items-center gap-2">
        <img src="/globe.svg" alt="Logo" className="w-8 h-8" />
        <span className="text-xl font-bold text-emerald-700 dark:text-emerald-300">NutrIA Pro</span>
      </div>
      <nav className="flex gap-4">
        <Link href="/nutricionista/configuracoes" className="rounded px-4 py-2 font-medium text-zinc-700 dark:text-zinc-200 hover:bg-emerald-100 dark:hover:bg-zinc-800 transition-colors">Configurações</Link>
        <button onClick={logout} className="rounded-full bg-red-500 hover:bg-red-600 text-white px-4 py-2 font-semibold transition-colors">Sair</button>
      </nav>
    </header>
  );
}
