"use client";
import React from 'react';

export default function Hero() {
  return (
    <section className="relative flex flex-col items-center justify-center min-h-[70vh] w-full bg-gradient-to-br from-green-100 via-white to-blue-100 dark:from-zinc-900 dark:via-black dark:to-zinc-800 py-20 px-4">
      <div className="absolute inset-0 pointer-events-none select-none opacity-10">
        <img src="/globe.svg" alt="Background globe" className="w-full h-full object-cover" />
      </div>
      <div className="relative z-10 flex flex-col items-center max-w-2xl text-center gap-8">
        <h1 className="text-5xl md:text-6xl font-extrabold bg-gradient-to-r from-green-600 via-blue-600 to-emerald-400 bg-clip-text text-transparent drop-shadow-lg">
          Transforme sua carreira com o NutrIA Pro
        </h1>
        <h2 className="text-2xl md:text-3xl font-medium text-zinc-700 dark:text-zinc-200">
          A plataforma definitiva para nutricionistas que querem crescer, automatizar e encantar seus clientes.
        </h2>
        <p className="text-lg md:text-xl text-zinc-600 dark:text-zinc-300 max-w-xl mx-auto">
          Automatize agendamentos, centralize atendimentos, aumente sua receita e tenha mais tempo para o que importa: cuidar dos seus pacientes. Junte-se a centenas de profissionais que já estão revolucionando sua rotina com o NutrIA Pro.
        </p>
        <div className="flex flex-col gap-2 mt-4">
          <span className="inline-block text-emerald-700 dark:text-emerald-300 font-semibold text-lg">Teste grátis por 14 dias</span>
          <a href="#cadastro" className="rounded-full bg-emerald-500 hover:bg-emerald-600 text-white px-8 py-4 font-bold text-xl shadow-lg transition-colors mt-2">Quero experimentar agora</a>
        </div>
      </div>
    </section>
  );
}
