"use client";

import React, { useState } from "react";

export default function ExamesResultados() {
  const [solicitacao, setSolicitacao] = useState("");
  const [resultados, setResultados] = useState<File[]>([]);
  const [historico, setHistorico] = useState<string[]>([]);
  const [analise, setAnalise] = useState("");
  const [recomendacoes, setRecomendacoes] = useState("");

  const handleUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    setResultados([...resultados, ...Array.from(e.target.files || [])]);
  };

  const analisarIA = () => {
    setAnalise("Análise automática: resultados dentro dos parâmetros. Sugestão: manter plano alimentar atual.");
    setRecomendacoes("Recomendações clínicas: aumentar ingestão de ferro, repetir exame em 3 meses.");
    setHistorico((prev) => [...prev, `Análise IA executada em ${new Date().toLocaleDateString("pt-BR")}`]);
  };

  return (
    <div className="mx-auto w-full max-w-6xl space-y-6">
      <section className="rounded-3xl border border-emerald-100 bg-white p-7 shadow-sm">
        <h1 className="text-3xl font-black text-zinc-900">Exames e Resultados</h1>
        <p className="mt-2 text-zinc-600">
          Central técnica para solicitação, upload e interpretação assistida de exames clínicos.
        </p>
      </section>

      <section className="grid gap-4 lg:grid-cols-[1.1fr_0.9fr]">
        <article className="rounded-2xl border border-zinc-200 bg-white p-6 shadow-sm">
          <div className="space-y-4">
            <div>
              <label className="mb-1 block text-sm font-semibold text-zinc-700">Solicitação de exames</label>
              <input
                value={solicitacao}
                onChange={(e) => setSolicitacao(e.target.value)}
                placeholder="Ex: hemograma, ferritina, vitamina D"
                className="w-full rounded-xl border border-zinc-200 bg-zinc-50 px-4 py-2.5 text-sm"
              />
            </div>
            <div>
              <label className="mb-1 block text-sm font-semibold text-zinc-700">Upload de resultados</label>
              <input type="file" multiple onChange={handleUpload} className="block w-full rounded-xl border border-zinc-200 bg-zinc-50 p-3 text-sm" />
              {resultados.length > 0 && (
                <ul className="mt-3 space-y-1 text-sm text-zinc-600">
                  {resultados.map((file, idx) => (
                    <li key={`${file.name}-${idx}`}>{file.name}</li>
                  ))}
                </ul>
              )}
            </div>
            <button
              onClick={analisarIA}
              className="rounded-xl bg-emerald-500 px-4 py-2.5 text-sm font-semibold text-white hover:bg-emerald-600"
            >
              Analisar com IA
            </button>
            {analise && <div className="rounded-xl border border-emerald-200 bg-emerald-50 p-4 text-sm text-emerald-800">{analise}</div>}
          </div>
        </article>

        <article className="rounded-2xl border border-zinc-200 bg-white p-6 shadow-sm">
          <h2 className="text-xl font-bold text-zinc-900">Histórico e recomendações</h2>
          <div className="mt-4 space-y-3">
            <div className="rounded-xl border border-zinc-200 bg-zinc-50 p-4">
              <p className="text-xs font-semibold uppercase tracking-wide text-zinc-500">Histórico</p>
              <ul className="mt-2 space-y-1 text-sm text-zinc-700">
                {historico.length === 0 ? <li>Nenhum exame registrado.</li> : historico.map((item) => <li key={item}>{item}</li>)}
              </ul>
            </div>
            <div className="rounded-xl border border-zinc-200 bg-zinc-50 p-4">
              <p className="text-xs font-semibold uppercase tracking-wide text-zinc-500">Recomendações clínicas</p>
              <textarea
                value={recomendacoes}
                onChange={(e) => setRecomendacoes(e.target.value)}
                placeholder="Ajustes, orientações e próximos passos"
                className="mt-2 h-28 w-full rounded-lg border border-zinc-200 bg-white px-3 py-2 text-sm"
              />
            </div>
          </div>
        </article>
      </section>
    </div>
  );
}
