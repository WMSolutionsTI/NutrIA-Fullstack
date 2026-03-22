"use client";
import React from "react";
import Link from "next/link";
import { useUser } from "@/context/UserContext";

export default function NutriNavbar() {
  const { logout, trial, trialExpired } = useUser();

  return (
    <header className="sticky top-0 z-30 flex w-full items-center justify-between border-b border-emerald-100 bg-white/85 px-4 py-3 backdrop-blur-xl md:px-6">
      <div className="flex items-center gap-2">
        <div className="rounded-xl bg-emerald-100 p-1.5">
          <img src="/globe.svg" alt="Logo" className="h-6 w-6" />
        </div>
        <div>
          <p className="text-sm font-black text-zinc-900 md:text-base">NutrIA Pro</p>
          <p className="hidden text-xs text-zinc-500 md:block">Painel da nutricionista</p>
        </div>
      </div>

      <nav className="flex items-center gap-2 md:gap-4">
        {trial && (
          <div
            className={`hidden rounded-full px-4 py-1 text-xs font-semibold md:block ${
              trialExpired
                ? "bg-red-100 text-red-700"
                : "bg-emerald-100 text-emerald-700"
            }`}
          >
            {trialExpired ? "Acesso premium pausado" : "Central IA ativa 24h"}
          </div>
        )}
        <Link
          href="/nutricionista/configuracoes"
          className="rounded-lg border border-zinc-200 px-3 py-1.5 text-sm font-semibold text-zinc-700 hover:bg-zinc-50"
        >
          Configurações
        </Link>
        <button
          onClick={logout}
          className="rounded-lg bg-zinc-900 px-3 py-1.5 text-sm font-semibold text-white hover:bg-zinc-800"
        >
          Sair
        </button>
      </nav>
    </header>
  );
}
