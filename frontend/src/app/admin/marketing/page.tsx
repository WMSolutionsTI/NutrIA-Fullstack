import React, { useState } from "react";

export default function CampanhasMarketing() {
  // Simulação de campanhas
  const [campanhas, setCampanhas] = useState([
    { nome: "Promoção de Lançamento", canal: "WhatsApp", status: "Ativa", conversao: 22 },
    { nome: "Webinar NutrIA-Pro", canal: "Instagram", status: "Finalizada", conversao: 15 },
  ]);
  const [novaCampanha, setNovaCampanha] = useState("");
  const [novoCanal, setNovoCanal] = useState("");

  const adicionarCampanha = () => {
    if (novaCampanha && novoCanal) {
      setCampanhas([...campanhas, { nome: novaCampanha, canal: novoCanal, status: "Ativa", conversao: 0 }]);
      setNovaCampanha("");
      setNovoCanal("");
    }
  };

  // Simulação de automação IA
  const automacaoIA = "Automação ativa: IA segmenta, dispara mensagens, monitora engajamento e ajusta campanhas.";

  return (
    <div className="min-h-screen bg-gradient-to-br from-pink-100 via-white to-blue-100 dark:from-zinc-900 dark:via-black dark:to-zinc-800 px-4 py-8">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-3xl font-bold text-pink-700 dark:text-pink-300 mb-8">Campanhas e Marketing</h1>
        {/* Criação de campanha */}
        <section className="mb-6">
          <h2 className="text-xl font-semibold mb-2">Criar Campanha</h2>
          <div className="flex gap-4">
            <input value={novaCampanha} onChange={e => setNovaCampanha(e.target.value)} placeholder="Nome da campanha" className="input" />
            <input value={novoCanal} onChange={e => setNovoCanal(e.target.value)} placeholder="Canal (WhatsApp, Instagram, Email)" className="input" />
            <button onClick={adicionarCampanha} className="rounded bg-pink-600 hover:bg-pink-700 text-white px-6 py-2 font-semibold shadow">Adicionar</button>
          </div>
        </section>
        {/* Tabela de campanhas */}
        <section className="mb-6">
          <h2 className="text-xl font-semibold mb-2">Campanhas Ativas</h2>
          <table className="w-full bg-white dark:bg-zinc-900 rounded shadow">
            <thead>
              <tr>
                <th className="py-2 px-4">Nome</th>
                <th className="py-2 px-4">Canal</th>
                <th className="py-2 px-4">Status</th>
                <th className="py-2 px-4">Conversão (%)</th>
              </tr>
            </thead>
            <tbody>
              {campanhas.map((c, idx) => (
                <tr key={idx}>
                  <td className="py-2 px-4">{c.nome}</td>
                  <td className="py-2 px-4">{c.canal}</td>
                  <td className="py-2 px-4">{c.status}</td>
                  <td className="py-2 px-4">{c.conversao}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </section>
        {/* Automação IA */}
        <section className="mb-6">
          <h2 className="text-xl font-semibold mb-2">Automação IA</h2>
          <div className="bg-white dark:bg-zinc-900 rounded p-4 shadow">
            <p>{automacaoIA}</p>
            <p>Integração Chatwoot e redes sociais: <span className="font-bold">Ativa</span></p>
          </div>
        </section>
        {/* Métricas de performance */}
        <section className="mb-6">
          <h2 className="text-xl font-semibold mb-2">Métricas de Performance</h2>
          <div className="bg-white dark:bg-zinc-900 rounded p-4 shadow">
            <p>Campanhas ativas: <span className="font-bold">{campanhas.filter(c => c.status === "Ativa").length}</span></p>
            <p>Taxa média de conversão: <span className="font-bold">{campanhas.length ? Math.round(campanhas.reduce((acc, c) => acc + c.conversao, 0) / campanhas.length) : 0}</span>%</p>
          </div>
        </section>
      </div>
    </div>
  );
}

// Estilos básicos para inputs
// Adicione ao seu CSS global:
// .input { border-radius: 0.5rem; border: 1px solid #d1d5db; padding: 0.5rem; background: #fff; color: #222; }
// .input:focus { outline: none; border-color: #ec4899; background: #fdf2f8; }