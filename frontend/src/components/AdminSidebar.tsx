"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

const links = [
  { href: "/admin/dashboard", label: "Dashboard" },
  { href: "/admin/nutricionistas", label: "Nutricionistas" },
  { href: "/admin/clientes", label: "Clientes" },
  { href: "/admin/mensagens", label: "Mensagens" },
  { href: "/admin/marketing", label: "Marketing" },
  { href: "/admin/planos", label: "Planos" },
  { href: "/admin/relatorios", label: "Relatórios" },
  { href: "/admin/contabilidade", label: "Contabilidade" },
  { href: "/admin/configuracoes", label: "Configurações" },
];

export default function AdminSidebar() {
  const pathname = usePathname();

  return (
    <aside className="hidden lg:flex flex-col w-72 border-r border-zinc-200 bg-white/90 backdrop-blur-xl p-6">
      <div className="flex items-center gap-3 mb-8">
        <img src="/globe.svg" alt="NutrIA Pro" className="w-10 h-10" />
        <div>
          <p className="text-lg font-black text-zinc-900">NutrIA Pro</p>
          <p className="text-xs text-zinc-500">Admin Control Center</p>
        </div>
      </div>
      <nav className="space-y-1">
        {links.map((link) => {
          const active = pathname === link.href;
          return (
            <Link
              key={link.href}
              href={link.href}
              className={`block rounded-xl px-4 py-2.5 text-sm font-semibold transition-all ${
                active
                  ? "bg-zinc-900 text-white shadow"
                  : "text-zinc-700 hover:bg-zinc-100"
              }`}
            >
              {link.label}
            </Link>
          );
        })}
      </nav>
      <div className="mt-auto rounded-2xl border border-emerald-200 bg-emerald-50 p-4">
        <p className="text-xs font-semibold text-emerald-800">Operação 24h</p>
        <p className="mt-1 text-xs text-emerald-700">
          Plataforma orientada a crescimento, retenção e escala comercial.
        </p>
      </div>
    </aside>
  );
}
