import React from "react";

const features = [
  {
    title: "Hub de Comunicação Unificado",
    description:
      "WhatsApp, Telegram, Instagram, Facebook, API e formulários integrados em uma única operação.",
  },
  {
    title: "Secretária IA com Contexto Nutricional",
    description:
      "Respostas personalizadas, follow-ups, lembretes e suporte ao atendimento humano quando necessário.",
  },
  {
    title: "Gestão de Inboxes por Plano",
    description:
      "Controle de limite, compra avulsa e acompanhamento de pendências de integração direto no painel.",
  },
  {
    title: "CRM Clínico e Relatórios",
    description:
      "Histórico de conversas, clientes, arquivos e inteligência para decisões comerciais e clínicas.",
  },
];

export default function Features() {
  return (
    <section className="w-full bg-white py-20">
      <div className="mx-auto max-w-7xl px-6 space-y-12">
        <div className="max-w-3xl">
          <p className="inline-flex rounded-full border border-zinc-200 bg-zinc-50 px-4 py-1 text-sm font-semibold text-zinc-700">
            Ecossistema completo de crescimento
          </p>
          <h2 className="mt-4 text-4xl font-black text-zinc-900">Tudo o que a sua operação precisa, no mesmo lugar.</h2>
          <p className="mt-4 text-lg text-zinc-600">
            Construído para nutricionistas que querem combinar excelência clínica com alta performance operacional.
          </p>
        </div>

        <div className="grid gap-5 md:grid-cols-2">
          {features.map((feature) => (
            <article
              key={feature.title}
              className="rounded-3xl border border-zinc-200 bg-zinc-50/70 p-6 shadow-[0_14px_30px_rgba(15,23,42,0.06)] hover:-translate-y-1 hover:shadow-[0_20px_40px_rgba(16,185,129,0.16)] transition-all"
            >
              <h3 className="text-2xl font-bold text-zinc-900">{feature.title}</h3>
              <p className="mt-3 text-zinc-600">{feature.description}</p>
            </article>
          ))}
        </div>

        <div className="rounded-3xl border border-emerald-100 bg-emerald-50/70 p-7 md:p-8">
          <h3 className="text-2xl font-black text-zinc-900">Uma estrutura equivalente a uma equipe completa, 24h por dia</h3>
          <ol className="mt-4 grid gap-3 md:grid-cols-2">
            {[
              "Secretária digital para atendimento, triagem e respostas rápidas.",
              "Assistente de agenda para encaixes, remarcações e confirmações.",
              "Apoio de relacionamento para acompanhamento e retenção contínua.",
              "Operação de comunicação para campanhas e reativação de leads.",
              "Organização de dados clínicos e histórico centralizado.",
              "Camada analítica para apoiar decisões estratégicas do negócio.",
            ].map((step, index) => (
              <li key={step} className="rounded-xl border border-emerald-200 bg-white px-4 py-3 text-zinc-700">
                <span className="font-bold text-emerald-700">Frente {index + 1}:</span> {step}
              </li>
            ))}
          </ol>
        </div>
      </div>
    </section>
  );
}
