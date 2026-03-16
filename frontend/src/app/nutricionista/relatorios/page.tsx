"use client";
import React from "react";

const MOCK_RELATORIOS = {
  consultas: 42,
  clientes: 30,
  faturamento: 8200.50,
  engajamento: 87,
  campanhas: 5,
};

export default function Relatorios() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-emerald-100 via-white to-blue-100 dark:from-zinc-900 dark:via-black dark:to-zinc-800 px-4 py-8">
      <div className="max-w-5xl mx-auto">
        <h1 className="text-3xl font-bold text-emerald-700 dark:text-emerald-300 mb-6">Relatórios</h1>
        <div className="grid md:grid-cols-3 gap-8 mb-8">
          <div className="bg-white dark:bg-zinc-900 rounded-xl shadow-lg p-6 border border-emerald-100 dark:border-zinc-800 flex flex-col items-center">
            <span className="text-2xl font-bold text-emerald-600 dark:text-emerald-200">{MOCK_RELATORIOS.consultas}</span>
            <span className="text-zinc-700 dark:text-zinc-200">Consultas realizadas</span>
          </div>
          <div className="bg-white dark:bg-zinc-900 rounded-xl shadow-lg p-6 border border-blue-100 dark:border-zinc-800 flex flex-col items-center">
            <span className="text-2xl font-bold text-blue-600 dark:text-blue-200">{MOCK_RELATORIOS.clientes}</span>
            <span className="text-zinc-700 dark:text-zinc-200">Clientes ativos</span>
          </div>
          <div className="bg-white dark:bg-zinc-900 rounded-xl shadow-lg p-6 border border-pink-100 dark:border-zinc-800 flex flex-col items-center">
            <span className="text-2xl font-bold text-pink-600 dark:text-pink-200">R$ {MOCK_RELATORIOS.faturamento.toFixed(2)}</span>
            <span className="text-zinc-700 dark:text-zinc-200">Faturamento (mês)</span>
          </div>
        </div>
        <div className="grid md:grid-cols-2 gap-8">
          <div className="bg-white dark:bg-zinc-900 rounded-xl shadow-lg p-6 border border-emerald-100 dark:border-zinc-800 flex flex-col items-center">
            <span className="text-2xl font-bold text-emerald-600 dark:text-emerald-200">{MOCK_RELATORIOS.engajamento}%</span>
            <span className="text-zinc-700 dark:text-zinc-200">Engajamento dos clientes</span>
          </div>
          <div className="bg-white dark:bg-zinc-900 rounded-xl shadow-lg p-6 border border-blue-100 dark:border-zinc-800 flex flex-col items-center">
            <span className="text-2xl font-bold text-blue-600 dark:text-blue-200">{MOCK_RELATORIOS.campanhas}</span>
            <span className="text-zinc-700 dark:text-zinc-200">Campanhas enviadas</span>
          </div>
        </div>
        <div className="mt-12 text-center text-zinc-500 dark:text-zinc-400 text-sm">
          * Relatórios detalhados e exportação estarão disponíveis em breve.
        </div>
      </div>
    </div>
  );
}
