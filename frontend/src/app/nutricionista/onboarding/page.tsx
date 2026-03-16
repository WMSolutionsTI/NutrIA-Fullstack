"use client";
import React from "react";

export default function NutriOnboarding() {
  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-gradient-to-br from-emerald-100 via-white to-blue-100 dark:from-zinc-900 dark:via-black dark:to-zinc-800 px-4 py-12">
      <div className="bg-white dark:bg-zinc-900 rounded-xl shadow-lg p-8 w-full max-w-2xl flex flex-col gap-6 border border-emerald-100 dark:border-zinc-800">
        <h1 className="text-3xl font-bold text-center text-emerald-700 dark:text-emerald-300 mb-2">Bem-vindo ao NutrIA Pro!</h1>
        <p className="text-lg text-zinc-700 dark:text-zinc-200 text-center">Seu ambiente está pronto para transformar sua rotina. Siga os passos abaixo para começar:</p>
        <ol className="list-decimal list-inside text-zinc-700 dark:text-zinc-200 text-lg space-y-2">
          <li>Configure sua secretária virtual (nome, prompt, horários, mensagens automáticas)</li>
          <li>Cadastre seus primeiros clientes</li>
          <li>Conecte seus canais de atendimento (WhatsApp, Instagram, e-mail...)</li>
          <li>Personalize seu calendário e horários de atendimento</li>
          <li>Explore o painel: mensagens, agenda, CRM, cobranças e relatórios</li>
        </ol>
        <a href="/nutricionista/painel" className="rounded-full bg-emerald-500 hover:bg-emerald-600 text-white px-8 py-4 font-bold text-xl shadow-lg transition-colors text-center mt-4">Ir para o painel</a>
      </div>
    </div>
  );
}
