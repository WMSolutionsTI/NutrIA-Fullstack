import React, { useState } from "react";

export default function ConfiguracoesIntegracoesAdmin() {
  // Simulação de integrações
  const [chatwoot, setChatwoot] = useState("Ativa");
  const [n8n, setN8n] = useState("Ativa");
  const [assas, setAssas] = useState("Ativa");
  const [workers, setWorkers] = useState("Ativos");
  const [seguranca, setSeguranca] = useState("OK");
  const [auditoria, setAuditoria] = useState(["Login admin 15/03/2026", "Configuração n8n atualizada"]);

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-100 via-white to-blue-100 dark:from-zinc-900 dark:via-black dark:to-zinc-800 px-4 py-8">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-3xl font-bold text-gray-700 dark:text-gray-300 mb-8">Configurações e Integrações Admin</h1>
        {/* Setup de integrações */}
        <section className="mb-6">
          <h2 className="text-xl font-semibold mb-2">Integrações</h2>
          <div className="grid grid-cols-2 gap-4">
            <div className="bg-white dark:bg-zinc-900 rounded p-4 shadow">
              <p className="font-bold">Chatwoot:</p>
              <p>{chatwoot}</p>
            </div>
            <div className="bg-white dark:bg-zinc-900 rounded p-4 shadow">
              <p className="font-bold">n8n:</p>
              <p>{n8n}</p>
            </div>
            <div className="bg-white dark:bg-zinc-900 rounded p-4 shadow">
              <p className="font-bold">Assas:</p>
              <p>{assas}</p>
            </div>
            <div className="bg-white dark:bg-zinc-900 rounded p-4 shadow">
              <p className="font-bold">Workers:</p>
              <p>{workers}</p>
            </div>
          </div>
        </section>
        {/* Segurança */}
        <section className="mb-6">
          <h2 className="text-xl font-semibold mb-2">Segurança</h2>
          <div className="bg-white dark:bg-zinc-900 rounded p-4 shadow">
            <p>Status: <span className="font-bold">{seguranca}</span></p>
          </div>
        </section>
        {/* Auditoria */}
        <section className="mb-6">
          <h2 className="text-xl font-semibold mb-2">Auditoria</h2>
          <ul className="bg-white dark:bg-zinc-900 rounded p-4 shadow">
            {auditoria.map((a, idx) => <li key={idx}>{a}</li>)}
          </ul>
        </section>
      </div>
    </div>
  );
}

// Estilos básicos para inputs
// Adicione ao seu CSS global:
// .input { border-radius: 0.5rem; border: 1px solid #d1d5db; padding: 0.5rem; background: #fff; color: #222; }
// .input:focus { outline: none; border-color: #6b7280; background: #f3f4f6; }