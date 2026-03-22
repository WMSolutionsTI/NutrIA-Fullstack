"use client";

const fluxo = {
  receita: 154320,
  despesas: 49650,
  saldo: 104670,
  mrr: 28740,
};

const eventos = [
  "Repasse de afiliados consolidado em 20/03/2026.",
  "Conciliação automática de 98,2% das cobranças concluída.",
  "2 faturas enterprise em análise de risco de churn.",
];

const previsoes = [
  { mes: "Abril/2026", valor: "R$ 171.000", variacao: "+11%" },
  { mes: "Maio/2026", valor: "R$ 182.500", variacao: "+6%" },
  { mes: "Junho/2026", valor: "R$ 195.900", variacao: "+7%" },
];

export default function ContabilidadeAdmin() {
  return (
    <div className="space-y-6">
      <section className="rounded-3xl border border-zinc-200 bg-white p-7 shadow-sm">
        <h1 className="text-3xl font-black text-zinc-900">Contabilidade e Receita</h1>
        <p className="mt-2 text-zinc-600">
          Visão financeira consolidada para previsibilidade de caixa e expansão sustentável.
        </p>
      </section>

      <section className="grid gap-4 md:grid-cols-4">
        <article className="rounded-2xl border border-emerald-200 bg-emerald-50 p-5">
          <p className="text-sm font-semibold text-emerald-700">Receita mensal</p>
          <p className="mt-1 text-3xl font-black text-emerald-900">R$ {fluxo.receita}</p>
        </article>
        <article className="rounded-2xl border border-rose-200 bg-rose-50 p-5">
          <p className="text-sm font-semibold text-rose-700">Despesas</p>
          <p className="mt-1 text-3xl font-black text-rose-900">R$ {fluxo.despesas}</p>
        </article>
        <article className="rounded-2xl border border-cyan-200 bg-cyan-50 p-5">
          <p className="text-sm font-semibold text-cyan-700">Saldo operacional</p>
          <p className="mt-1 text-3xl font-black text-cyan-900">R$ {fluxo.saldo}</p>
        </article>
        <article className="rounded-2xl border border-violet-200 bg-violet-50 p-5">
          <p className="text-sm font-semibold text-violet-700">MRR</p>
          <p className="mt-1 text-3xl font-black text-violet-900">R$ {fluxo.mrr}</p>
        </article>
      </section>

      <section className="grid gap-4 lg:grid-cols-[1.3fr_0.7fr]">
        <article className="rounded-2xl border border-zinc-200 bg-white p-6 shadow-sm">
          <div className="flex items-center justify-between">
            <h2 className="text-xl font-bold text-zinc-900">Eventos de conciliação</h2>
            <button className="rounded-xl bg-zinc-900 px-4 py-2 text-sm font-semibold text-white hover:bg-zinc-800">
              Exportar DRE
            </button>
          </div>
          <ul className="mt-4 space-y-2 text-sm text-zinc-700">
            {eventos.map((evento) => (
              <li key={evento} className="rounded-xl border border-zinc-200 bg-zinc-50 px-4 py-2.5">
                {evento}
              </li>
            ))}
          </ul>
        </article>

        <article className="rounded-2xl border border-zinc-200 bg-white p-6 shadow-sm">
          <h2 className="text-xl font-bold text-zinc-900">Previsão de receita</h2>
          <div className="mt-4 space-y-3">
            {previsoes.map((p) => (
              <div key={p.mes} className="rounded-xl border border-zinc-200 bg-zinc-50 p-3">
                <p className="text-xs font-semibold uppercase tracking-wide text-zinc-500">{p.mes}</p>
                <p className="mt-1 text-lg font-bold text-zinc-900">{p.valor}</p>
                <p className="text-xs font-semibold text-emerald-600">{p.variacao}</p>
              </div>
            ))}
          </div>
        </article>
      </section>
    </div>
  );
}
