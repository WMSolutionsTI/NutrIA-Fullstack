"use client";

import React from "react";

interface HeroProps {
  onTrialClick: () => void;
  onNutriLoginClick: () => void;
}

export default function Hero({ onTrialClick, onNutriLoginClick }: HeroProps) {
  return (
    <section className="relative overflow-hidden w-full">
      <div className="absolute inset-0 bg-[radial-gradient(circle_at_15%_20%,#86efac55,transparent_35%),radial-gradient(circle_at_85%_0%,#22d3ee44,transparent_45%),linear-gradient(135deg,#f4fff7_0%,#ecf8ff_55%,#f8fff5_100%)]" />
      <div className="absolute -left-24 top-28 h-64 w-64 rounded-full bg-emerald-200/40 blur-3xl animate-pulse" />
      <div className="absolute right-0 -top-24 h-80 w-80 rounded-full bg-cyan-200/40 blur-3xl animate-pulse" />

      <div className="relative mx-auto max-w-7xl px-6 py-20 md:py-24 grid gap-10 lg:grid-cols-[1.1fr_0.9fr] items-center">
        <div>
          <p className="inline-flex rounded-full border border-emerald-200 bg-white/80 px-4 py-1 text-sm font-semibold text-emerald-700">
            NutrIA Pro • Plataforma de crescimento para nutricionistas
          </p>
          <h1 className="mt-6 text-5xl md:text-6xl font-black tracking-tight text-zinc-900 leading-tight">
            Atendimento nutricional moderno, automatizado e encantador.
          </h1>
          <p className="mt-5 text-lg text-zinc-600 max-w-2xl">
            Transforme sua rotina com secretária IA, caixa de entrada omnicanal e gestão completa de clientes,
            agenda, planos e relatórios em uma experiência premium pronta para escala.
          </p>

          <div className="mt-9 flex flex-col sm:flex-row gap-4">
            <button
              onClick={onTrialClick}
              className="group rounded-2xl bg-emerald-600 hover:bg-emerald-700 text-white px-7 py-4 font-bold text-lg shadow-[0_18px_38px_rgba(5,150,105,0.35)] transition-all hover:-translate-y-1"
            >
              Testar 14 dias grátis
              <span className="block text-sm font-medium text-emerald-100">Sem cartão na largada</span>
            </button>
            <button
              onClick={onNutriLoginClick}
              className="rounded-2xl border border-zinc-300 bg-white hover:bg-zinc-50 px-7 py-4 font-semibold text-zinc-800 transition-all hover:-translate-y-1"
            >
              Entrar na plataforma
            </button>
          </div>

          <div className="mt-8 grid grid-cols-1 sm:grid-cols-3 gap-3">
            <div className="rounded-2xl border border-white/70 bg-white/80 p-4 backdrop-blur-sm">
              <p className="text-2xl font-black text-zinc-900">+500</p>
              <p className="text-sm text-zinc-600">contas por instância Chatwoot</p>
            </div>
            <div className="rounded-2xl border border-white/70 bg-white/80 p-4 backdrop-blur-sm">
              <p className="text-2xl font-black text-zinc-900">14 dias</p>
              <p className="text-sm text-zinc-600">com acesso total ao produto</p>
            </div>
            <div className="rounded-2xl border border-white/70 bg-white/80 p-4 backdrop-blur-sm">
              <p className="text-2xl font-black text-zinc-900">24/7</p>
              <p className="text-sm text-zinc-600">suporte operacional inteligente</p>
            </div>
          </div>
        </div>

        <div className="relative">
          <div className="rounded-3xl border border-emerald-100 bg-white/90 p-7 shadow-[0_30px_90px_rgba(15,23,42,0.18)] backdrop-blur-xl">
            <div className="flex items-center gap-3">
              <img src="/globe.svg" alt="NutrIA Pro logo" className="h-10 w-10" />
              <div>
                <p className="font-bold text-zinc-900">Sua equipe digital de alta performance</p>
                <p className="text-sm text-zinc-500">Operação contínua, com padrão premium de atendimento.</p>
              </div>
            </div>
            <div className="mt-6 space-y-3">
              {[
                "Recepção e qualificação inicial de novos clientes",
                "Agendamentos, confirmações e lembretes automáticos",
                "Atendimento inteligente em múltiplos canais",
                "Follow-ups estratégicos e recuperação de clientes inativos",
                "Apoio operacional constante para a nutricionista",
              ].map((item) => (
                <div key={item} className="rounded-xl border border-zinc-200 bg-zinc-50 px-4 py-3 text-sm text-zinc-700">
                  {item}
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
