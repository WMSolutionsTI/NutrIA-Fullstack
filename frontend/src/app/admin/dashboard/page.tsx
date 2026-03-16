import React from "react";

export default function DashboardAdmin() {
  // Simulação de dados
  const metricas = {
    tenants: 12,
    nutricionistas: 34,
    clientes: 420,
    mensagens: 12000,
    receita: 15000,
    despesas: 5000,
    saldo: 10000,
  };
  const alertas = ["Pagamento pendente de 2 clientes", "Nova integração disponível: n8n"];

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-100 via-white to-emerald-100 dark:from-zinc-900 dark:via-black dark:to-zinc-800 px-4 py-8">
      <div className="max-w-5xl mx-auto">
        <h1 className="text-3xl font-bold text-blue-700 dark:text-blue-300 mb-8">Dashboard Admin</h1>
        {/* Métricas principais */}
        <section className="mb-6">
          <div className="grid grid-cols-3 gap-4">
            <div className="bg-white dark:bg-zinc-900 rounded p-4 shadow">
              <p className="font-bold">Tenants:</p>
              <p>{metricas.tenants}</p>
            </div>
            <div className="bg-white dark:bg-zinc-900 rounded p-4 shadow">
              <p className="font-bold">Nutricionistas:</p>
              <p>{metricas.nutricionistas}</p>
            </div>
            <div className="bg-white dark:bg-zinc-900 rounded p-4 shadow">
              <p className="font-bold">Clientes:</p>
              <p>{metricas.clientes}</p>
            </div>
            <div className="bg-white dark:bg-zinc-900 rounded p-4 shadow col-span-3">
              <p className="font-bold">Mensagens:</p>
              <p>{metricas.mensagens}</p>
            </div>
          </div>
        </section>
        {/* Contabilidade */}
        <section className="mb-6">
          <h2 className="text-xl font-semibold mb-2">Contabilidade</h2>
          <div className="grid grid-cols-3 gap-4">
            <div className="bg-white dark:bg-zinc-900 rounded p-4 shadow">
              <p className="font-bold">Receita:</p>
              <p>R$ {metricas.receita}</p>
            </div>
            <div className="bg-white dark:bg-zinc-900 rounded p-4 shadow">
              <p className="font-bold">Despesas:</p>
              <p>R$ {metricas.despesas}</p>
            </div>
            <div className="bg-white dark:bg-zinc-900 rounded p-4 shadow">
              <p className="font-bold">Saldo:</p>
              <p>R$ {metricas.saldo}</p>
            </div>
          </div>
        </section>
        {/* Alertas */}
        <section className="mb-6">
          <h2 className="text-xl font-semibold mb-2">Alertas</h2>
          <ul className="bg-blue-100 dark:bg-zinc-800 rounded p-4 shadow">
            {alertas.map((a, idx) => <li key={idx}>{a}</li>)}
          </ul>
        </section>
        {/* Navegação para áreas de gestão */}
        <section className="mb-6">
          <h2 className="text-xl font-semibold mb-2">Gestão</h2>
          <div className="flex flex-wrap gap-4">
            <a href="/admin/nutricionistas" className="rounded bg-blue-600 hover:bg-blue-700 text-white px-6 py-2 font-semibold shadow">Nutricionistas</a>
            <a href="/admin/clientes" className="rounded bg-emerald-500 hover:bg-emerald-600 text-white px-6 py-2 font-semibold shadow">Clientes</a>
            <a href="/admin/mensagens" className="rounded bg-pink-500 hover:bg-pink-600 text-white px-6 py-2 font-semibold shadow">Mensagens</a>
            <a href="/admin/planos" className="rounded bg-yellow-500 hover:bg-yellow-600 text-white px-6 py-2 font-semibold shadow">Planos e Assinaturas</a>
            <a href="/admin/relatorios" className="rounded bg-indigo-500 hover:bg-indigo-600 text-white px-6 py-2 font-semibold shadow">Relatórios e Analytics</a>
            <a href="/admin/configuracoes" className="rounded bg-gray-500 hover:bg-gray-600 text-white px-6 py-2 font-semibold shadow">Configurações</a>
            <a href="/admin/contabilidade" className="rounded bg-green-700 hover:bg-green-800 text-white px-6 py-2 font-semibold shadow">Contabilidade</a>
          </div>
        </section>
      </div>
    </div>
  );
}