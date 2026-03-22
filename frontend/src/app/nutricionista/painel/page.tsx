"use client";

import Link from "next/link";
import { useMemo } from "react";

import { useUser } from "@/context/UserContext";

const cards = [
  {
    title: "Caixa de Entrada",
    description: "Gerencie inboxes, pendências de integração e atendimento omnicanal.",
    href: "/nutricionista/caixa-de-entrada",
  },
  {
    title: "Agenda Inteligente",
    description: "Disponibilidade, lembretes e confirmação de consultas em fluxo automático.",
    href: "/nutricionista/agenda",
  },
  {
    title: "Clientes e Prontuário",
    description: "Histórico completo, evolução e arquivos para atendimento personalizado.",
    href: "/nutricionista/clientes",
  },
  {
    title: "Mensagens",
    description: "Converse em tempo real com clientes e com sua secretária IA.",
    href: "/nutricionista/mensagens",
  },
];

export default function NutriPainel() {
  const { user, trial, trialExpired } = useUser();

  const trialMessage = useMemo(() => {
    if (!trial) return "Você está em plano ativo sem período de teste registrado.";
    if (trialExpired) {
      return "Seu acesso premium está pausado. Reative para continuar com toda a operação inteligente 24h.";
    }
    return "Sua operação inteligente está ativa com atendimento, agenda, relacionamento e gestão integrada.";
  }, [trial, trialExpired]);

  return (
    <div className="space-y-6">
      <section className="rounded-3xl border border-zinc-200 bg-white p-8 shadow-[0_24px_80px_rgba(15,23,42,0.10)]">
        <h1 className="text-4xl font-black tracking-tight text-zinc-900">Painel da Nutricionista</h1>
        <p className="mt-2 text-zinc-600">
          {user ? `Olá, ${user.nome}.` : "Olá."} Aqui está a visão executiva da sua operação.
        </p>
      </section>

      <section className="rounded-2xl border border-cyan-200 bg-cyan-50 p-6">
        <h2 className="text-2xl font-black text-cyan-900">Configuração inicial da secretária</h2>
        <p className="mt-2 text-sm text-cyan-800">
          Preencha todo o contexto do seu negócio para ativar atendimento de alta performance: especialidade, público-alvo,
          agenda, precificação, pacotes, canais e integrações.
        </p>
        <div className="mt-4 flex flex-wrap gap-3">
          <Link href="/nutricionista/onboarding" className="rounded-xl bg-cyan-700 px-4 py-2 text-sm font-semibold text-white hover:bg-cyan-800">
            Configurar agora
          </Link>
          <Link href="/nutricionista/caixa-de-entrada" className="rounded-xl border border-cyan-300 bg-white px-4 py-2 text-sm font-semibold text-cyan-900 hover:bg-cyan-100">
            Configurar primeira inbox
          </Link>
        </div>
      </section>

      <section
        className={`rounded-2xl border p-5 ${
          trialExpired ? "border-red-200 bg-red-50 text-red-800" : "border-emerald-200 bg-emerald-50 text-emerald-800"
        }`}
      >
        <p className="font-semibold">{trialMessage}</p>
        {trialExpired && (
          <Link
            href="/nutricionista/cobrancas?trial=expired"
            className="inline-flex mt-3 rounded-xl bg-red-600 hover:bg-red-700 text-white px-4 py-2 text-sm font-semibold transition-colors"
          >
            Ativar assinatura agora
          </Link>
        )}
      </section>

      <section className="grid gap-5 md:grid-cols-2">
        {cards.map((card) => (
          <Link
            key={card.title}
            href={trialExpired && card.href !== "/nutricionista/cobrancas" ? "/nutricionista/cobrancas?trial=expired" : card.href}
            className="group rounded-2xl border border-zinc-200 bg-white p-6 shadow-[0_16px_40px_rgba(15,23,42,0.08)] hover:-translate-y-1 hover:shadow-[0_20px_50px_rgba(16,185,129,0.18)] transition-all"
          >
            <h2 className="text-2xl font-bold text-zinc-900">{card.title}</h2>
            <p className="mt-2 text-zinc-600">{card.description}</p>
            <span className="mt-4 inline-flex text-sm font-semibold text-emerald-700 group-hover:text-emerald-800">
              Acessar modulo
            </span>
          </Link>
        ))}
      </section>
    </div>
  );
}
