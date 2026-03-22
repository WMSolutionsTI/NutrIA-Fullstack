"use client";

import React, { useState } from "react";

type CalculosNutricionais = {
  calorias: number;
  macros: {
    carbo: number;
    proteina: number;
    gordura: number;
  };
  micronutrientes: {
    ferro: number;
    calcio: number;
  };
};

export default function PlanoAlimentar() {
  const [objetivo, setObjetivo] = useState("");
  const [preferencias, setPreferencias] = useState("");
  const [restricoes, setRestricoes] = useState("");
  const [plano, setPlano] = useState("");
  const [calculos, setCalculos] = useState<CalculosNutricionais>({
    calorias: 0,
    macros: { carbo: 0, proteina: 0, gordura: 0 },
    micronutrientes: { ferro: 0, calcio: 0 },
  });
  const [observacoes, setObservacoes] = useState("");

  const gerarPlanoIA = () => {
    setPlano("Plano alimentar gerado automaticamente (exemplo)");
    setCalculos({
      calorias: 2000,
      macros: { carbo: 250, proteina: 120, gordura: 60 },
      micronutrientes: { ferro: 18, calcio: 1000 },
    });
  };

  return (
    <div className="mx-auto w-full max-w-6xl space-y-6">
      <section className="rounded-3xl border border-emerald-100 bg-white p-7 shadow-sm">
        <h1 className="text-3xl font-black text-zinc-900">Plano Alimentar Inteligente</h1>
        <p className="mt-2 text-zinc-600">
          Estruture protocolos personalizados com apoio da IA para acelerar produção técnica e padronizar qualidade.
        </p>
      </section>

      <section className="grid gap-4 lg:grid-cols-[1.1fr_0.9fr]">
        <article className="rounded-2xl border border-zinc-200 bg-white p-6 shadow-sm">
          <div className="space-y-4">
            <div>
              <label className="mb-1 block text-sm font-semibold text-zinc-700">Objetivo nutricional</label>
              <input
                value={objetivo}
                onChange={(e) => setObjetivo(e.target.value)}
                placeholder="Ex: perda de peso, ganho de massa"
                className="w-full rounded-xl border border-zinc-200 bg-zinc-50 px-4 py-2.5 text-sm"
              />
            </div>
            <div>
              <label className="mb-1 block text-sm font-semibold text-zinc-700">Preferências alimentares</label>
              <input
                value={preferencias}
                onChange={(e) => setPreferencias(e.target.value)}
                placeholder="Preferências"
                className="w-full rounded-xl border border-zinc-200 bg-zinc-50 px-4 py-2.5 text-sm"
              />
            </div>
            <div>
              <label className="mb-1 block text-sm font-semibold text-zinc-700">Restrições e alergias</label>
              <input
                value={restricoes}
                onChange={(e) => setRestricoes(e.target.value)}
                placeholder="Restrições"
                className="w-full rounded-xl border border-zinc-200 bg-zinc-50 px-4 py-2.5 text-sm"
              />
            </div>
            <button
              onClick={gerarPlanoIA}
              className="rounded-xl bg-emerald-500 px-4 py-2.5 text-sm font-semibold text-white hover:bg-emerald-600"
            >
              Gerar plano com IA
            </button>
            <div>
              <label className="mb-1 block text-sm font-semibold text-zinc-700">Plano alimentar</label>
              <textarea
                value={plano}
                onChange={(e) => setPlano(e.target.value)}
                placeholder="Plano alimentar detalhado"
                className="h-36 w-full rounded-xl border border-zinc-200 bg-zinc-50 px-4 py-2.5 text-sm"
              />
            </div>
            <div>
              <label className="mb-1 block text-sm font-semibold text-zinc-700">Observações clínicas</label>
              <textarea
                value={observacoes}
                onChange={(e) => setObservacoes(e.target.value)}
                placeholder="Recomendações e ajustes"
                className="h-24 w-full rounded-xl border border-zinc-200 bg-zinc-50 px-4 py-2.5 text-sm"
              />
            </div>
          </div>
        </article>

        <article className="rounded-2xl border border-zinc-200 bg-white p-6 shadow-sm">
          <h2 className="text-xl font-bold text-zinc-900">Cálculos nutricionais</h2>
          <div className="mt-4 space-y-3">
            <div className="rounded-xl border border-zinc-200 bg-zinc-50 p-4">
              <p className="text-xs font-semibold uppercase tracking-wide text-zinc-500">Calorias</p>
              <p className="mt-1 text-2xl font-black text-zinc-900">{calculos.calorias} kcal</p>
            </div>
            <div className="rounded-xl border border-zinc-200 bg-zinc-50 p-4">
              <p className="text-xs font-semibold uppercase tracking-wide text-zinc-500">Macronutrientes</p>
              <p className="mt-1 text-sm text-zinc-700">
                Carboidratos {calculos.macros.carbo || 0}g • Proteína {calculos.macros.proteina || 0}g • Gordura{" "}
                {calculos.macros.gordura || 0}g
              </p>
            </div>
            <div className="rounded-xl border border-zinc-200 bg-zinc-50 p-4">
              <p className="text-xs font-semibold uppercase tracking-wide text-zinc-500">Micronutrientes</p>
              <p className="mt-1 text-sm text-zinc-700">
                Ferro {calculos.micronutrientes.ferro || 0}mg • Cálcio {calculos.micronutrientes.calcio || 0}mg
              </p>
            </div>
          </div>
        </article>
      </section>
    </div>
  );
}
