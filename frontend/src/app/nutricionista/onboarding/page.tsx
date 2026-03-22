"use client";
import Link from "next/link";
import { useRouter } from "next/navigation";
import React, { useState } from "react";

import { configurarIntegracaoAsaas, salvarConfiguracaoInicial } from "@/lib/api/auth";
import { ApiError } from "@/lib/api/client";

export default function NutriOnboarding() {
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [saved, setSaved] = useState(false);
  const [modalidades, setModalidades] = useState<{ online: boolean; presencial: boolean }>({
    online: false,
    presencial: false,
  });
  const [form, setForm] = useState({
    sobre_nutricionista: "",
    tipos_atendimento: "",
    especialidade: "",
    publico_alvo: "",
    periodo_trabalho: "",
    disponibilidade_agenda: "",
    duracao_consulta_minutos: 60,
    preco_consulta: "",
    pacotes_atendimento: "",
    metodo_atendimento: "",
    endereco_consulta_presencial: "",
    instagram: "",
    facebook: "",
    telefone_profissional: "",
    site: "",
    contatos_adicionais: "",
    google_agenda_configurada: false,
    asaas_configurada: false,
    primeira_inbox_configurada: false,
    asaas_api_key: "",
    asaas_api_url: "",
    asaas_webhook_token: "",
    asaas_wallet_id: "",
  });

  function handleChange(
    e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>
  ) {
    const { name, value } = e.target;
    setForm((prev) => ({
      ...prev,
      [name]: name === "duracao_consulta_minutos" ? Number(value || 0) : value,
    }));
  }

  function handleToggle(e: React.ChangeEvent<HTMLInputElement>) {
    const { name, checked } = e.target;
    setForm((prev) => ({ ...prev, [name]: checked }));
  }

  function handleModalidadeToggle(e: React.ChangeEvent<HTMLInputElement>) {
    const { name, checked } = e.target;
    if (name !== "online" && name !== "presencial") return;
    setModalidades((prev) => ({ ...prev, [name]: checked }));
  }

  function serializeModalidades(selected: { online: boolean; presencial: boolean }): string {
    if (selected.online && selected.presencial) return "online,presencial";
    if (selected.online) return "online";
    if (selected.presencial) return "presencial";
    return "";
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    try {
      setLoading(true);
      setError("");
      const metodoAtendimento = serializeModalidades(modalidades);
      if (!metodoAtendimento) {
        setError("Selecione ao menos uma modalidade de atendimento (online ou presencial).");
        return;
      }
      if (form.asaas_configurada || form.asaas_api_key.trim()) {
        if (!form.asaas_api_key.trim()) {
          setError("Informe a API Key da sua conta Asaas para ativar cobrança individual.");
          return;
        }
        await configurarIntegracaoAsaas({
          api_key: form.asaas_api_key.trim(),
          api_url: form.asaas_api_url.trim() || undefined,
          webhook_token: form.asaas_webhook_token.trim() || undefined,
          wallet_id: form.asaas_wallet_id.trim() || undefined,
        });
      }
      await salvarConfiguracaoInicial({
        sobre_nutricionista: form.sobre_nutricionista,
        tipos_atendimento: form.tipos_atendimento,
        especialidade: form.especialidade,
        publico_alvo: form.publico_alvo,
        periodo_trabalho: form.periodo_trabalho,
        disponibilidade_agenda: form.disponibilidade_agenda,
        duracao_consulta_minutos: form.duracao_consulta_minutos,
        preco_consulta: form.preco_consulta,
        pacotes_atendimento: form.pacotes_atendimento,
        metodo_atendimento: metodoAtendimento,
        endereco_consulta_presencial: form.endereco_consulta_presencial,
        instagram: form.instagram,
        facebook: form.facebook,
        telefone_profissional: form.telefone_profissional,
        site: form.site,
        contatos_adicionais: form.contatos_adicionais,
        google_agenda_configurada: form.google_agenda_configurada,
        asaas_configurada: form.asaas_configurada,
        primeira_inbox_configurada: form.primeira_inbox_configurada,
      });
      setSaved(true);
      router.push("/nutricionista/painel");
      router.refresh();
    } catch (err) {
      if (err instanceof ApiError) {
        setError(err.detail);
      } else {
        setError("Não foi possível salvar a configuração inicial.");
      }
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="mx-auto w-full max-w-6xl space-y-6">
      <section className="rounded-3xl border border-emerald-100 bg-white p-7 shadow-sm">
        <h1 className="text-3xl font-black text-zinc-900 md:text-4xl">Ativação da sua operação</h1>
        <p className="mt-2 max-w-3xl text-zinc-600">
          Configure sua secretária com contexto completo, integrações e ofertas comerciais para iniciar a operação 24h com alto padrão de atendimento.
        </p>
      </section>

      <form onSubmit={handleSubmit} className="rounded-2xl border border-zinc-200 bg-white p-6 shadow-sm">
        <div className="grid gap-4 md:grid-cols-2">
          <textarea name="sobre_nutricionista" value={form.sobre_nutricionista} onChange={handleChange} placeholder="Sobre a nutricionista e proposta de valor" className="h-28 rounded-xl border border-zinc-200 bg-zinc-50 px-4 py-2.5 text-sm md:col-span-2" />
          <input name="tipos_atendimento" value={form.tipos_atendimento} onChange={handleChange} placeholder="Tipos de atendimento" className="rounded-xl border border-zinc-200 bg-zinc-50 px-4 py-2.5 text-sm" />
          <input name="especialidade" value={form.especialidade} onChange={handleChange} placeholder="Especialidade" className="rounded-xl border border-zinc-200 bg-zinc-50 px-4 py-2.5 text-sm" />
          <input name="publico_alvo" value={form.publico_alvo} onChange={handleChange} placeholder="Público-alvo" className="rounded-xl border border-zinc-200 bg-zinc-50 px-4 py-2.5 text-sm" />
          <input name="periodo_trabalho" value={form.periodo_trabalho} onChange={handleChange} placeholder="Período de trabalho" className="rounded-xl border border-zinc-200 bg-zinc-50 px-4 py-2.5 text-sm" />
          <input name="disponibilidade_agenda" value={form.disponibilidade_agenda} onChange={handleChange} placeholder="Disponibilidade de agenda" className="rounded-xl border border-zinc-200 bg-zinc-50 px-4 py-2.5 text-sm" />
          <input name="duracao_consulta_minutos" type="number" min={10} max={240} value={form.duracao_consulta_minutos} onChange={handleChange} placeholder="Duração padrão da consulta (minutos)" className="rounded-xl border border-zinc-200 bg-zinc-50 px-4 py-2.5 text-sm" />
          <input name="preco_consulta" value={form.preco_consulta} onChange={handleChange} placeholder="Preço da consulta" className="rounded-xl border border-zinc-200 bg-zinc-50 px-4 py-2.5 text-sm" />
          <textarea name="pacotes_atendimento" value={form.pacotes_atendimento} onChange={handleChange} placeholder="Pacotes de atendimento: descrição detalhada e valores" className="h-28 rounded-xl border border-zinc-200 bg-zinc-50 px-4 py-2.5 text-sm md:col-span-2" />
          <div className="rounded-xl border border-zinc-200 bg-zinc-50 px-4 py-3 text-sm">
            <p className="text-xs font-semibold uppercase tracking-wide text-zinc-500">Modalidades de atendimento</p>
            <div className="mt-2 flex flex-wrap gap-4 text-sm text-zinc-700">
              <label className="flex items-center gap-2">
                <input type="checkbox" name="online" checked={modalidades.online} onChange={handleModalidadeToggle} />
                Online
              </label>
              <label className="flex items-center gap-2">
                <input type="checkbox" name="presencial" checked={modalidades.presencial} onChange={handleModalidadeToggle} />
                Presencial
              </label>
            </div>
          </div>
          <input name="endereco_consulta_presencial" value={form.endereco_consulta_presencial} onChange={handleChange} placeholder="Endereço consulta presencial" className="rounded-xl border border-zinc-200 bg-zinc-50 px-4 py-2.5 text-sm" />
          <input name="instagram" value={form.instagram} onChange={handleChange} placeholder="Instagram" className="rounded-xl border border-zinc-200 bg-zinc-50 px-4 py-2.5 text-sm" />
          <input name="facebook" value={form.facebook} onChange={handleChange} placeholder="Facebook" className="rounded-xl border border-zinc-200 bg-zinc-50 px-4 py-2.5 text-sm" />
          <input name="telefone_profissional" value={form.telefone_profissional} onChange={handleChange} placeholder="Telefone profissional" className="rounded-xl border border-zinc-200 bg-zinc-50 px-4 py-2.5 text-sm" />
          <input name="site" value={form.site} onChange={handleChange} placeholder="Site" className="rounded-xl border border-zinc-200 bg-zinc-50 px-4 py-2.5 text-sm" />
          <textarea name="contatos_adicionais" value={form.contatos_adicionais} onChange={handleChange} placeholder="Outras informações de contato" className="h-24 rounded-xl border border-zinc-200 bg-zinc-50 px-4 py-2.5 text-sm md:col-span-2" />
          <input name="asaas_api_key" value={form.asaas_api_key} onChange={handleChange} placeholder="Asaas API Key (conta da nutricionista)" className="rounded-xl border border-zinc-200 bg-zinc-50 px-4 py-2.5 text-sm md:col-span-2" />
          <input name="asaas_api_url" value={form.asaas_api_url} onChange={handleChange} placeholder="Asaas API URL (opcional)" className="rounded-xl border border-zinc-200 bg-zinc-50 px-4 py-2.5 text-sm" />
          <input name="asaas_wallet_id" value={form.asaas_wallet_id} onChange={handleChange} placeholder="Asaas Wallet ID (opcional)" className="rounded-xl border border-zinc-200 bg-zinc-50 px-4 py-2.5 text-sm" />
          <input name="asaas_webhook_token" value={form.asaas_webhook_token} onChange={handleChange} placeholder="Asaas Webhook Token (opcional)" className="rounded-xl border border-zinc-200 bg-zinc-50 px-4 py-2.5 text-sm md:col-span-2" />
        </div>

        <div className="mt-5 rounded-2xl border border-zinc-200 bg-zinc-50 p-4">
          <p className="text-sm font-semibold text-zinc-700">Checklist de integração</p>
          <p className="mt-1 text-xs text-zinc-500">
            Google Agenda: conecte no menu Agenda para sincronizar disponibilidade.
            <br />
            Asaas: acesse Cobranças e informe API Key/Wallet ID para cobrança automática.
            <br />
            Primeira inbox: acesse Caixa de Entrada e finalize a integração inicial.
          </p>
          <div className="mt-3 space-y-2 text-sm text-zinc-700">
            <label className="flex items-center gap-2">
              <input type="checkbox" name="google_agenda_configurada" checked={form.google_agenda_configurada} onChange={handleToggle} />
              Google Agenda integrada
            </label>
            <label className="flex items-center gap-2">
              <input type="checkbox" name="asaas_configurada" checked={form.asaas_configurada} onChange={handleToggle} />
              Conta Asaas integrada
            </label>
            <label className="flex items-center gap-2">
              <input type="checkbox" name="primeira_inbox_configurada" checked={form.primeira_inbox_configurada} onChange={handleToggle} />
              Primeira caixa de entrada configurada
            </label>
          </div>
        </div>

        {error && <div className="mt-4 rounded-lg border border-red-200 bg-red-50 p-3 text-sm text-red-700">{error}</div>}
        {saved && <div className="mt-4 rounded-lg border border-emerald-200 bg-emerald-50 p-3 text-sm text-emerald-700">Configuração salva com sucesso.</div>}

        <div className="mt-5 flex flex-wrap gap-3">
          <button disabled={loading} type="submit" className="rounded-xl bg-emerald-500 px-5 py-2.5 text-sm font-semibold text-white hover:bg-emerald-600 disabled:opacity-60">
            {loading ? "Salvando..." : "Finalizar configuração inicial"}
          </button>
          <Link href="/nutricionista/caixa-de-entrada" className="rounded-xl border border-zinc-300 bg-white px-5 py-2.5 text-sm font-semibold text-zinc-700 hover:bg-zinc-50">
            Ir para caixa de entrada
          </Link>
        </div>
      </form>
    </div>
  );
}
