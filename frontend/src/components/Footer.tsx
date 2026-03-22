import React from "react";

export default function Footer() {
  return (
    <footer className="w-full border-t border-zinc-200 bg-zinc-950 text-zinc-200">
      <div className="mx-auto max-w-7xl px-6 py-12 grid gap-8 md:grid-cols-3">
        <div>
          <div className="flex items-center gap-2">
            <img src="/globe.svg" alt="NutrIA Pro" className="w-8 h-8" />
            <span className="text-xl font-bold text-emerald-300">NutrIA Pro</span>
          </div>
          <p className="mt-3 text-sm text-zinc-400">
            Plataforma SaaS de excelência para nutricionistas com atendimento omnicanal e automações inteligentes.
          </p>
        </div>
        <div>
          <p className="font-semibold text-white">Produto</p>
          <ul className="mt-3 space-y-2 text-sm text-zinc-400">
            <li>Teste grátis de 14 dias</li>
            <li>Gestão de inboxes e Chatwoot</li>
            <li>Secretária IA especializada</li>
          </ul>
        </div>
        <div>
          <p className="font-semibold text-white">Jurídico</p>
          <div className="mt-3 flex flex-col gap-2 text-sm">
            <a href="#" className="text-zinc-400 hover:text-emerald-300 transition-colors">Política de Privacidade</a>
            <a href="#" className="text-zinc-400 hover:text-emerald-300 transition-colors">Termos de Uso</a>
            <a href="#" className="text-zinc-400 hover:text-emerald-300 transition-colors">Suporte e Contato</a>
          </div>
        </div>
      </div>
      <div className="border-t border-zinc-800 py-4 text-center text-xs text-zinc-500">
        © {new Date().getFullYear()} NutrIA Pro. Todos os direitos reservados.
      </div>
    </footer>
  );
}
