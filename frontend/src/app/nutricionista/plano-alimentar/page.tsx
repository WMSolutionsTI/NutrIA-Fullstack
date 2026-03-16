import React, { useState } from "react";

export default function PlanoAlimentar() {
  // Estados para campos principais
  const [objetivo, setObjetivo] = useState("");
  const [preferencias, setPreferencias] = useState("");
  const [restricoes, setRestricoes] = useState("");
  const [plano, setPlano] = useState("");
  const [calculos, setCalculos] = useState({ calorias: 0, macros: {}, micronutrientes: {} });
  const [observacoes, setObservacoes] = useState("");

  // Simulação de geração automática por IA
  const gerarPlanoIA = () => {
    // Aqui será feita a chamada para o agente de IA
    setPlano("Plano alimentar gerado automaticamente (exemplo)");
    setCalculos({ calorias: 2000, macros: { carbo: 250, proteina: 120, gordura: 60 }, micronutrientes: { ferro: 18, calcio: 1000 } });
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-emerald-100 via-white to-blue-100 dark:from-zinc-900 dark:via-black dark:to-zinc-800 px-4 py-8">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-3xl font-bold text-blue-700 dark:text-blue-300 mb-8">Plano Alimentar Inteligente</h1>
        {/* Dados do paciente (importados do prontuário) */}
        <section className="mb-6">
          <h2 className="text-xl font-semibold mb-2">Objetivo Nutricional</h2>
          <input value={objetivo} onChange={e => setObjetivo(e.target.value)} placeholder="Ex: perda de peso, ganho de massa" className="input w-full" />
        </section>
        <section className="mb-6">
          <h2 className="text-xl font-semibold mb-2">Preferências e Restrições</h2>
          <input value={preferencias} onChange={e => setPreferencias(e.target.value)} placeholder="Preferências alimentares" className="input w-full mb-2" />
          <input value={restricoes} onChange={e => setRestricoes(e.target.value)} placeholder="Restrições, intolerâncias, alergias" className="input w-full" />
        </section>
        {/* Geração automática por IA */}
        <section className="mb-6">
          <button onClick={gerarPlanoIA} className="rounded bg-blue-600 hover:bg-blue-700 text-white px-6 py-2 font-semibold shadow">Gerar Plano Automático (IA)</button>
        </section>
        {/* Plano semanal/dia a dia */}
        <section className="mb-6">
          <h2 className="text-xl font-semibold mb-2">Plano Alimentar</h2>
          <textarea value={plano} onChange={e => setPlano(e.target.value)} placeholder="Plano alimentar detalhado (editável)" className="input w-full h-32" />
        </section>
        {/* Cálculo automático */}
        <section className="mb-6">
          <h2 className="text-xl font-semibold mb-2">Cálculos Nutricionais</h2>
          <div className="bg-white dark:bg-zinc-900 rounded p-4 shadow">
            <p>Calorias: <span className="font-bold">{calculos.calorias}</span> kcal</p>
            <p>Macros: Carboidratos <span className="font-bold">{calculos.macros.carbo || 0}</span>g, Proteína <span className="font-bold">{calculos.macros.proteina || 0}</span>g, Gordura <span className="font-bold">{calculos.macros.gordura || 0}</span>g</p>
            <p>Micronutrientes: Ferro <span className="font-bold">{calculos.micronutrientes.ferro || 0}</span>mg, Cálcio <span className="font-bold">{calculos.micronutrientes.calcio || 0}</span>mg</p>
          </div>
        </section>
        {/* Observações */}
        <section className="mb-6">
          <h2 className="text-xl font-semibold mb-2">Observações</h2>
          <textarea value={observacoes} onChange={e => setObservacoes(e.target.value)} placeholder="Recomendações clínicas, ajustes" className="input w-full h-16" />
        </section>
      </div>
    </div>
  );
}

// Estilos básicos para inputs
// Adicione ao seu CSS global:
// .input { border-radius: 0.5rem; border: 1px solid #d1d5db; padding: 0.5rem; background: #fff; color: #222; }
// .input:focus { outline: none; border-color: #3b82f6; background: #f0f6ff; }