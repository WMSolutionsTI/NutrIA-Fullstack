import Link from "next/link";

const metricas = {
  tenants: 12,
  nutricionistas: 34,
  clientes: 420,
  mensagens: 12000,
  receita: 15000,
  despesas: 5000,
  saldo: 10000,
};

const alertas = [
  "2 assinaturas com pagamento pendente.",
  "Nova integração disponível para automações n8n.",
  "Taxa de resposta em WhatsApp subiu 14% na última semana.",
];

const quickLinks = [
  { href: "/admin/nutricionistas", label: "Nutricionistas" },
  { href: "/admin/clientes", label: "Clientes" },
  { href: "/admin/mensagens", label: "Mensagens" },
  { href: "/admin/marketing", label: "Marketing" },
  { href: "/admin/planos", label: "Planos" },
  { href: "/admin/relatorios", label: "Relatórios" },
];

export default function DashboardAdmin() {
  return (
    <div className="space-y-6">
      <section className="rounded-3xl border border-zinc-200 bg-white p-8 shadow-[0_20px_60px_rgba(15,23,42,0.08)]">
        <h1 className="text-4xl font-black text-zinc-900">Dashboard Executivo</h1>
        <p className="mt-2 text-zinc-600">
          Centro de comando para crescimento de vendas, eficiência operacional e retenção de clientes.
        </p>
      </section>

      <section className="grid gap-4 md:grid-cols-4">
        {[
          { label: "Tenants ativos", value: metricas.tenants },
          { label: "Nutricionistas", value: metricas.nutricionistas },
          { label: "Clientes finais", value: metricas.clientes },
          { label: "Mensagens processadas", value: metricas.mensagens },
        ].map((item) => (
          <article key={item.label} className="rounded-2xl border border-zinc-200 bg-white p-5 shadow-sm">
            <p className="text-sm text-zinc-500">{item.label}</p>
            <p className="mt-1 text-3xl font-black text-zinc-900">{item.value}</p>
          </article>
        ))}
      </section>

      <section className="grid gap-4 md:grid-cols-3">
        <article className="rounded-2xl border border-emerald-200 bg-emerald-50 p-5">
          <p className="text-sm font-semibold text-emerald-700">Receita</p>
          <p className="mt-1 text-3xl font-black text-emerald-900">R$ {metricas.receita}</p>
        </article>
        <article className="rounded-2xl border border-rose-200 bg-rose-50 p-5">
          <p className="text-sm font-semibold text-rose-700">Despesas</p>
          <p className="mt-1 text-3xl font-black text-rose-900">R$ {metricas.despesas}</p>
        </article>
        <article className="rounded-2xl border border-cyan-200 bg-cyan-50 p-5">
          <p className="text-sm font-semibold text-cyan-700">Saldo operacional</p>
          <p className="mt-1 text-3xl font-black text-cyan-900">R$ {metricas.saldo}</p>
        </article>
      </section>

      <section className="grid gap-4 lg:grid-cols-[1.2fr_0.8fr]">
        <article className="rounded-2xl border border-zinc-200 bg-white p-6 shadow-sm">
          <h2 className="text-xl font-bold text-zinc-900">Alertas de operação</h2>
          <ul className="mt-4 space-y-2 text-sm text-zinc-700">
            {alertas.map((alerta) => (
              <li key={alerta} className="rounded-xl border border-zinc-200 bg-zinc-50 px-4 py-2.5">
                {alerta}
              </li>
            ))}
          </ul>
        </article>

        <article className="rounded-2xl border border-zinc-200 bg-white p-6 shadow-sm">
          <h2 className="text-xl font-bold text-zinc-900">Ações rápidas</h2>
          <div className="mt-4 grid grid-cols-2 gap-2">
            {quickLinks.map((link) => (
              <Link
                key={link.href}
                href={link.href}
                className="rounded-xl border border-zinc-200 bg-zinc-50 px-3 py-2 text-center text-sm font-semibold text-zinc-800 hover:bg-zinc-100 transition-colors"
              >
                {link.label}
              </Link>
            ))}
          </div>
        </article>
      </section>
    </div>
  );
}
