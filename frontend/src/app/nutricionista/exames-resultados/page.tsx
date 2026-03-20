"use client";

import React, { useState } from "react";

export default function ExamesResultados() {
  const [solicitacao, setSolicitacao] = useState("");
  const [resultados, setResultados] = useState<File[]>([]);
  const [historico, setHistorico] = useState<string[]>([]);
  const [analise, setAnalise] = useState("");
  const [recomendacoes, setRecomendacoes] = useState("");

  // Simulação de upload
  const handleUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    setResultados([...resultados, ...Array.from(e.target.files || [])]);
  };

  // Simulação de análise automática por IA
  const analisarIA = () => {
    setAnalise("Análise automática: resultados dentro dos parâmetros. Sugestão: manter plano alimentar atual.");
    setRecomendacoes("Recomendações clínicas: aumentar ingestão de ferro, repetir exame em 3 meses.");
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-pink-100 via-white to-blue-100 dark:from-zinc-900 dark:via-black dark:to-zinc-800 px-4 py-8">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-3xl font-bold text-pink-700 dark:text-pink-300 mb-8">Exames e Resultados</h1>
        {/* Solicitação de exames */}
        <section className="mb-6">
          <h2 className="text-xl font-semibold mb-2">Solicitação de Exames</h2>
          <input value={solicitacao} onChange={e => setSolicitacao(e.target.value)} placeholder="Exames a solicitar (ex: hemograma, ferritina)" className="input w-full" />
        </section>
        {/* Upload de resultados */}
        <section className="mb-6">
          <h2 className="text-xl font-semibold mb-2">Upload de Resultados</h2>
          <input type="file" multiple onChange={handleUpload} className="input" />
          <ul className="mt-2">
            {resultados.map((file, idx) => (
              <li key={idx}>{file.name}</li>
            ))}
          </ul>
        </section>
        {/* Histórico de exames */}
        <section className="mb-6">
          <h2 className="text-xl font-semibold mb-2">Histórico de Exames</h2>
          <ul className="bg-white dark:bg-zinc-900 rounded p-4 shadow">
            {historico.length === 0 ? <li>Nenhum exame registrado.</li> : historico.map((item, idx) => (
              <li key={idx}>{item}</li>
            ))}
          </ul>
        </section>
        {/* Análise automática por IA */}
        <section className="mb-6">
          <button onClick={analisarIA} className="rounded bg-pink-600 hover:bg-pink-700 text-white px-6 py-2 font-semibold shadow">Analisar Automaticamente (IA)</button>
          {analise && <div className="mt-4 bg-pink-100 dark:bg-zinc-800 rounded p-4 shadow"><p>{analise}</p></div>}
        </section>
        {/* Recomendações clínicas */}
        <section className="mb-6">
          <h2 className="text-xl font-semibold mb-2">Recomendações Clínicas</h2>
          <textarea value={recomendacoes} onChange={e => setRecomendacoes(e.target.value)} placeholder="Ajustes, orientações, próximos passos" className="input w-full h-16" />
        </section>
      </div>
    </div>
  );
}

// Estilos básicos para inputs
// Adicione ao seu CSS global:
// .input { border-radius: 0.5rem; border: 1px solid #d1d5db; padding: 0.5rem; background: #fff; color: #222; }
// .input:focus { outline: none; border-color: #ec4899; background: #fdf2f8; }