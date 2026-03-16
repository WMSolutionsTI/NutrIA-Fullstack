"use client";
import React from "react";
import Link from "next/link";

const links = [
  { href: "/nutricionista/painel", label: "Painel" },
  { href: "/nutricionista/clientes", label: "Clientes" },
  { href: "/nutricionista/agenda", label: "Agenda" },
  { href: "/nutricionista/mensagens", label: "Mensagens" },
  { href: "/nutricionista/campanhas", label: "Campanhas" },
  { href: "/nutricionista/cobrancas", label: "Cobranças" },
  { href: "/nutricionista/relatorios", label: "Relatórios" },
  { href: "/nutricionista/configuracoes", label: "Configurações" },
];

export default function NutriSidebar() {
  return (
    <aside className="hidden md:flex flex-col w-60 min-h-screen bg-white dark:bg-zinc-900 border-r border-zinc-100 dark:border-zinc-800 py-8 px-4 gap-2 shadow-lg">
      <div className="mb-8 flex flex-col items-center">
        <img src="/globe.svg" alt="Logo" className="w-12 h-12 mb-2" />
        <span className="font-bold text-lg text-emerald-700 dark:text-emerald-300">NutrIA Pro</span>
      </div>
      <nav className="flex flex-col gap-2">
        {links.map(link => (
          <Link key={link.href} href={link.href} className="rounded px-4 py-2 font-medium text-zinc-700 dark:text-zinc-200 hover:bg-emerald-100 dark:hover:bg-zinc-800 transition-colors">
            {link.label}
          </Link>
        ))}
      </nav>
    </aside>
  );
}
