"use client";
import Link from "next/link";
import { useRouter } from "next/navigation";
import React, { useState } from "react";

import { salvarConfiguracaoInicial } from "@/lib/api/auth";
import { ApiError } from "@/lib/api/client";

export default function NutriOnboarding() {
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [saved, setSaved] = useState(false);
  const [form, setForm] = useState({
    sobre_nutricionista: "",
    tipos_atendimento: "",
    especialidade: "",
    publico_alvo: "",
    periodo_trabalho: "",
    disponibilidade_agenda: "",
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
  });

  function handleChange(
    e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>
  ) {
    const { name, value } = e.target;
    setForm((prev) => ({ ...prev, [name]: value }));
  }

  function handleToggle(e: React.ChangeEvent<HTMLInputElement>) {
    const { name, checked } = e.target;
    setForm((prev) => ({ ...prev, [name]: checked }));
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    try {
      setLoading(true);
      setError("");
      await salvarConfiguracaoInicial(form);
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
          <input name="preco_consulta" value={form.preco_consulta} onChange={handleChange} placeholder="Preço da consulta" className="rounded-xl border border-zinc-200 bg-zinc-50 px-4 py-2.5 text-sm" />
          <textarea name="pacotes_atendimento" value={form.pacotes_atendimento} onChange={handleChange} placeholder="Pacotes de atendimento: descrição detalhada e valores" className="h-28 rounded-xl border border-zinc-200 bg-zinc-50 px-4 py-2.5 text-sm md:col-span-2" />
          <select name="metodo_atendimento" value={form.metodo_atendimento} onChange={handleChange} className="rounded-xl border border-zinc-200 bg-zinc-50 px-4 py-2.5 text-sm">
            <option value="">Método de atendimento</option>
            <option value="online">Online</option>
            <option value="presencial">Presencial</option>
            <option value="hibrido">Online e presencial</option>
          </select>
          <input name="endereco_consulta_presencial" value={form.endereco_consulta_presencial} onChange={handleChange} placeholder="Endereço consulta presencial" className="rounded-xl border border-zinc-200 bg-zinc-50 px-4 py-2.5 text-sm" />
          <input name="instagram" value={form.instagram} onChange={handleChange} placeholder="Instagram" className="rounded-xl border border-zinc-200 bg-zinc-50 px-4 py-2.5 text-sm" />
          <input name="facebook" value={form.facebook} onChange={handleChange} placeholder="Facebook" className="rounded-xl border border-zinc-200 bg-zinc-50 px-4 py-2.5 text-sm" />
          <input name="telefone_profissional" value={form.telefone_profissional} onChange={handleChange} placeholder="Telefone profissional" className="rounded-xl border border-zinc-200 bg-zinc-50 px-4 py-2.5 text-sm" />
          <input name="site" value={form.site} onChange={handleChange} placeholder="Site" className="rounded-xl border border-zinc-200 bg-zinc-50 px-4 py-2.5 text-sm" />
          <textarea name="contatos_adicionais" value={form.contatos_adicionais} onChange={handleChange} placeholder="Outras informações de contato" className="h-24 rounded-xl border border-zinc-200 bg-zinc-50 px-4 py-2.5 text-sm md:col-span-2" />
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
