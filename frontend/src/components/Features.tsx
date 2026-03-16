import React from 'react';

export default function Features() {
  return (
    <section className="w-full max-w-5xl mx-auto py-16 px-4 grid md:grid-cols-2 gap-12">
      <div>
        <h3 className="text-2xl font-bold mb-4 text-emerald-700 dark:text-emerald-300">Por que escolher o NutrIA Pro?</h3>
        <ul className="space-y-4 text-zinc-700 dark:text-zinc-200 text-lg">
          <li><b>Automação total</b> de mensagens, agendamentos e cobranças</li>
          <li><b>Centralização</b> de todos os canais de atendimento</li>
          <li><b>Gestão de clientes</b> e histórico clínico completo</li>
          <li><b>Relatórios inteligentes</b> para decisões estratégicas</li>
          <li><b>Segurança</b> e privacidade de dados multi-tenant</li>
        </ul>
      </div>
      <div className="flex flex-col gap-6">
        <div className="bg-white/80 dark:bg-zinc-900/80 rounded-xl shadow-lg p-6 flex flex-col gap-2 border border-emerald-100 dark:border-zinc-800">
          <span className="text-emerald-600 dark:text-emerald-300 font-bold">+ Central de Mensagens Omnicanal</span>
          <span className="text-zinc-600 dark:text-zinc-300">WhatsApp, Instagram, E-mail e mais em um só lugar</span>
        </div>
        <div className="bg-white/80 dark:bg-zinc-900/80 rounded-xl shadow-lg p-6 flex flex-col gap-2 border border-blue-100 dark:border-zinc-800">
          <span className="text-blue-600 dark:text-blue-300 font-bold">+ Agendamento Inteligente</span>
          <span className="text-zinc-600 dark:text-zinc-300">Calendário integrado, lembretes automáticos e confirmação instantânea</span>
        </div>
        <div className="bg-white/80 dark:bg-zinc-900/80 rounded-xl shadow-lg p-6 flex flex-col gap-2 border border-pink-100 dark:border-zinc-800">
          <span className="text-pink-600 dark:text-pink-300 font-bold">+ CRM e Relatórios</span>
          <span className="text-zinc-600 dark:text-zinc-300">Histórico completo, métricas de engajamento e financeiro</span>
        </div>
      </div>
    </section>
  );
}
