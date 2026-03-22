"use client";

const integracoes = [
  { nome: "Chatwoot Cloud", status: "Operacional", latencia: "98ms" },
  { nome: "n8n Orchestrator", status: "Operacional", latencia: "121ms" },
  { nome: "Asaas Billing", status: "Operacional", latencia: "143ms" },
  { nome: "Workers IA", status: "Escalando", latencia: "89ms" },
];

const auditoria = [
  "21/03/2026 08:30 - Rotação de token API concluída.",
  "20/03/2026 18:05 - Atualização de regras de webhook WhatsApp.",
  "20/03/2026 09:11 - Backup incremental validado com sucesso.",
];

export default function ConfiguracoesIntegracoesAdmin() {
  return (
    <div className="space-y-6">
      <section className="rounded-3xl border border-zinc-200 bg-white p-7 shadow-sm">
        <h1 className="text-3xl font-black text-zinc-900">Configurações e Integrações</h1>
        <p className="mt-2 text-zinc-600">
          Governança técnica da operação: conectores, segurança e observabilidade da plataforma.
        </p>
      </section>

      <section className="grid gap-4 md:grid-cols-2">
        {integracoes.map((item) => (
          <article key={item.nome} className="rounded-2xl border border-zinc-200 bg-white p-5 shadow-sm">
            <p className="text-sm text-zinc-500">{item.nome}</p>
            <p className="mt-1 text-xl font-black text-zinc-900">{item.status}</p>
            <p className="mt-2 text-sm text-cyan-700">Latência média: {item.latencia}</p>
          </article>
        ))}
      </section>

      <section className="grid gap-4 lg:grid-cols-[1fr_1fr]">
        <article className="rounded-2xl border border-zinc-200 bg-white p-6 shadow-sm">
          <h2 className="text-xl font-bold text-zinc-900">Segurança da conta master</h2>
          <div className="mt-4 space-y-2 text-sm text-zinc-700">
            <p className="rounded-xl border border-zinc-200 bg-zinc-50 px-4 py-2.5">
              MFA administrativo: <span className="font-semibold text-emerald-700">Ativo</span>
            </p>
            <p className="rounded-xl border border-zinc-200 bg-zinc-50 px-4 py-2.5">
              Criptografia em repouso: <span className="font-semibold text-emerald-700">AES-256</span>
            </p>
            <p className="rounded-xl border border-zinc-200 bg-zinc-50 px-4 py-2.5">
              Monitoramento anti-fraude: <span className="font-semibold text-emerald-700">Ativo 24h</span>
            </p>
          </div>
        </article>

        <article className="rounded-2xl border border-zinc-200 bg-white p-6 shadow-sm">
          <h2 className="text-xl font-bold text-zinc-900">Auditoria recente</h2>
          <ul className="mt-4 space-y-2 text-sm text-zinc-700">
            {auditoria.map((evento) => (
              <li key={evento} className="rounded-xl border border-zinc-200 bg-zinc-50 px-4 py-2.5">
                {evento}
              </li>
            ))}
          </ul>
        </article>
      </section>
    </div>
  );
}
