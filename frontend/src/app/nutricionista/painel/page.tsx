"use client";
import React from "react";

export default function NutriPainel() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-emerald-100 via-white to-blue-100 dark:from-zinc-900 dark:via-black dark:to-zinc-800 px-4 py-8">
      <div className="max-w-6xl mx-auto">
        <h1 className="text-4xl font-bold text-emerald-700 dark:text-emerald-300 mb-8">Painel do Nutricionista</h1>
        <div className="grid md:grid-cols-3 gap-8">
          {/* Central de Mensagens */}
          <div className="bg-white dark:bg-zinc-900 rounded-xl shadow-lg p-6 border border-emerald-100 dark:border-zinc-800 flex flex-col gap-2">
            <h2 className="text-xl font-semibold text-emerald-600 dark:text-emerald-200 mb-2">Central de Mensagens</h2>
            <ul className="text-zinc-700 dark:text-zinc-200 text-base list-disc ml-4">
              <li>Gerencie conversas de WhatsApp, Instagram, e-mail e mais</li>
              <li>Histórico completo de interações</li>
              <li>Respostas automáticas e follow-ups</li>
            </ul>
            <button className="mt-4 rounded bg-emerald-500 hover:bg-emerald-600 text-white px-4 py-2 font-semibold">Acessar Mensagens</button>
          </div>
          {/* Agendamento e Consultas */}
          <div className="bg-white dark:bg-zinc-900 rounded-xl shadow-lg p-6 border border-blue-100 dark:border-zinc-800 flex flex-col gap-2">
            <h2 className="text-xl font-semibold text-emerald-600 dark:text-emerald-200 mb-2">Agendamento e Consultas</h2>
            <ul className="text-zinc-700 dark:text-zinc-200 text-base list-disc ml-4">
              <li>Calendário integrado e confirmação automática</li>
              <li>Gestão de consultas e anotações clínicas</li>
              <li>Envio de planos alimentares e materiais</li>
            </ul>
            <button className="mt-4 rounded bg-emerald-500 hover:bg-emerald-600 text-white px-4 py-2 font-semibold">Ver Consultas</button>
          </div>
          {/* CRM e Relatórios */}
          <div className="bg-white dark:bg-zinc-900 rounded-xl shadow-lg p-6 border border-pink-100 dark:border-zinc-800 flex flex-col gap-2">
            <h2 className="text-xl font-semibold text-emerald-600 dark:text-emerald-200 mb-2">CRM e Relatórios</h2>
            <ul className="text-zinc-700 dark:text-zinc-200 text-base list-disc ml-4">
              <li>Histórico de clientes, consultas e arquivos</li>
              <li>Métricas de engajamento e financeiro</li>
              <li>Campanhas e automações inteligentes</li>
            </ul>
            <button className="mt-4 rounded bg-emerald-500 hover:bg-emerald-600 text-white px-4 py-2 font-semibold">Acessar CRM</button>
          </div>
        </div>
      </div>
    </div>
  );
}
