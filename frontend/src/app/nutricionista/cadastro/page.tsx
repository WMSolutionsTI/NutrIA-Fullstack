"use client";

import Link from "next/link";
import React, { useEffect, useMemo, useState } from "react";

import { ApiError } from "@/lib/api/client";
import { obterStatusAssinatura, solicitarCheckoutAssinatura, solicitarTrial } from "@/lib/api/auth";

const PLAN_VALUES: Record<string, number> = {
  basic: 197,
  pro: 397,
  enterprise: 997,
};

export default function NutriCadastro() {
  const [mode, setMode] = useState<"trial" | "assinatura">("assinatura");
  const [trialForm, setTrialForm] = useState({
    nome: "",
    email: "",
    telefone: "",
  });
  const [checkoutForm, setCheckoutForm] = useState({
    nome: "",
    email: "",
    telefone: "",
    documento: "",
    plano_nome: "pro",
    billing_type: "PIX" as "PIX" | "BOLETO" | "CREDIT_CARD",
  });
  const [checkout, setCheckout] = useState<{
    pagamentoId: string;
    paymentLink?: string;
    pixQrCode?: string;
    paymentStatus: string;
    provisioned: boolean;
  } | null>(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [requested, setRequested] = useState(false);

  const selectedPlanValue = useMemo(() => PLAN_VALUES[checkoutForm.plano_nome] ?? PLAN_VALUES.pro, [checkoutForm.plano_nome]);

  useEffect(() => {
    if (!checkout?.pagamentoId || checkout.provisioned) return;
    const timer = window.setInterval(async () => {
      try {
        const status = await obterStatusAssinatura(checkout.pagamentoId);
        setCheckout((prev) =>
          prev
            ? {
                ...prev,
                paymentStatus: status.payment_status,
                provisioned: status.provisioned,
              }
            : prev
        );
      } catch {
        // mantém polling resiliente sem quebrar a tela pública
      }
    }, 10000);
    return () => window.clearInterval(timer);
  }, [checkout?.pagamentoId, checkout?.provisioned]);

  function handleTrialChange(e: React.ChangeEvent<HTMLInputElement>) {
    setTrialForm({ ...trialForm, [e.target.name]: e.target.value });
  }

  function handleCheckoutChange(
    e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>
  ) {
    setCheckoutForm({ ...checkoutForm, [e.target.name]: e.target.value });
  }

  async function handleSubmitTrial(e: React.FormEvent) {
    e.preventDefault();
    if (!trialForm.nome || !trialForm.email || !trialForm.telefone) {
      setError("Preencha nome, telefone e e-mail.");
      return;
    }

    try {
      setLoading(true);
      setError("");
      await solicitarTrial(trialForm);
      setRequested(true);
    } catch (err) {
      if (err instanceof ApiError) {
        setError(err.detail);
      } else {
        setError("Não foi possível solicitar seu cadastro de trial.");
      }
    } finally {
      setLoading(false);
    }
  }

  async function handleSubmitCheckout(e: React.FormEvent) {
    e.preventDefault();
    if (!checkoutForm.nome || !checkoutForm.email || !checkoutForm.telefone) {
      setError("Preencha nome, telefone e e-mail para contratar.");
      return;
    }
    try {
      setLoading(true);
      setError("");
      const result = await solicitarCheckoutAssinatura({
        nome: checkoutForm.nome,
        email: checkoutForm.email,
        telefone: checkoutForm.telefone,
        documento: checkoutForm.documento || undefined,
        plano_nome: checkoutForm.plano_nome,
        valor: selectedPlanValue,
        billing_type: checkoutForm.billing_type,
      });
      setCheckout({
        pagamentoId: result.pagamento_id,
        paymentLink: result.payment_link,
        pixQrCode: result.pix_qrcode,
        paymentStatus: "pendente",
        provisioned: false,
      });
    } catch (err) {
      if (err instanceof ApiError) {
        setError(err.detail);
      } else {
        setError("Não foi possível criar a cobrança da assinatura.");
      }
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="min-h-screen bg-[radial-gradient(circle_at_15%_20%,#c6f6d544,transparent_35%),radial-gradient(circle_at_85%_0%,#99f6e444,transparent_45%),linear-gradient(130deg,#f4fff7_0%,#eef9ff_55%,#f8fff9_100%)] px-4 py-10 md:py-16">
      <div className="mx-auto max-w-6xl grid gap-8 lg:grid-cols-[1.2fr_1fr]">
        <section className="rounded-3xl border border-emerald-100 bg-white/90 backdrop-blur-xl shadow-[0_24px_80px_rgba(16,185,129,0.12)] p-8 md:p-10">
          <p className="inline-flex items-center rounded-full border border-emerald-200 bg-emerald-50 px-4 py-1 text-sm font-semibold text-emerald-700">
            Ativação da Plataforma NutrIA Pro
          </p>
          <h1 className="mt-5 text-3xl md:text-4xl font-black text-zinc-900">
            Contrate ou teste o NutrIA Pro
          </h1>
          <p className="mt-3 text-zinc-600">
            Fluxo de contratação pública integrado ao checkout: após pagamento confirmado, a conta é provisionada automaticamente.
          </p>
          <div className="mt-6 rounded-2xl border border-cyan-200 bg-cyan-50 p-4 text-cyan-900">
            No primeiro login, você trocará a senha e em seguida completará seu cadastro com CPF obrigatório e endereço.
          </div>
          {requested && (
            <div className="mt-4 rounded-2xl border border-blue-200 bg-blue-50 p-4 text-blue-900">
              Solicitação recebida. Verifique seu e-mail para acessar com a senha temporária.
            </div>
          )}
        </section>

        <form
          onSubmit={mode === "trial" ? handleSubmitTrial : handleSubmitCheckout}
          className="rounded-3xl border border-zinc-200/80 bg-white/95 backdrop-blur-xl shadow-[0_24px_80px_rgba(15,23,42,0.10)] p-7 md:p-8 flex flex-col gap-5"
        >
          <div className="grid grid-cols-2 gap-2 rounded-xl border border-zinc-200 bg-zinc-50 p-1">
            <button
              type="button"
              onClick={() => setMode("assinatura")}
              className={`rounded-lg px-3 py-2 text-sm font-semibold ${
                mode === "assinatura" ? "bg-white text-emerald-700 shadow-sm" : "text-zinc-600"
              }`}
            >
              Contratar agora
            </button>
            <button
              type="button"
              onClick={() => setMode("trial")}
              className={`rounded-lg px-3 py-2 text-sm font-semibold ${
                mode === "trial" ? "bg-white text-emerald-700 shadow-sm" : "text-zinc-600"
              }`}
            >
              Trial 14 dias
            </button>
          </div>

          <h2 className="text-2xl font-bold text-zinc-900">
            {mode === "trial" ? "Cadastro inicial trial" : "Checkout de assinatura"}
          </h2>
          <input
            name="nome"
            type="text"
            placeholder="Nome completo"
            className="rounded-xl px-4 py-3 border border-zinc-200 bg-zinc-50 focus:outline-none focus:ring-2 focus:ring-emerald-300"
            value={mode === "trial" ? trialForm.nome : checkoutForm.nome}
            onChange={mode === "trial" ? handleTrialChange : handleCheckoutChange}
          />
          <input
            name="telefone"
            type="tel"
            placeholder="Telefone com WhatsApp"
            className="rounded-xl px-4 py-3 border border-zinc-200 bg-zinc-50 focus:outline-none focus:ring-2 focus:ring-emerald-300"
            value={mode === "trial" ? trialForm.telefone : checkoutForm.telefone}
            onChange={mode === "trial" ? handleTrialChange : handleCheckoutChange}
          />
          <input
            name="email"
            type="email"
            placeholder="E-mail profissional"
            className="rounded-xl px-4 py-3 border border-zinc-200 bg-zinc-50 focus:outline-none focus:ring-2 focus:ring-emerald-300"
            value={mode === "trial" ? trialForm.email : checkoutForm.email}
            onChange={mode === "trial" ? handleTrialChange : handleCheckoutChange}
          />

          {mode === "assinatura" && (
            <>
              <input
                name="documento"
                type="text"
                placeholder="CPF/CNPJ (opcional para checkout)"
                className="rounded-xl px-4 py-3 border border-zinc-200 bg-zinc-50 focus:outline-none focus:ring-2 focus:ring-emerald-300"
                value={checkoutForm.documento}
                onChange={handleCheckoutChange}
              />
              <div className="grid grid-cols-2 gap-3">
                <select
                  name="plano_nome"
                  className="rounded-xl px-4 py-3 border border-zinc-200 bg-zinc-50 focus:outline-none focus:ring-2 focus:ring-emerald-300"
                  value={checkoutForm.plano_nome}
                  onChange={handleCheckoutChange}
                >
                  <option value="basic">Plano Basic</option>
                  <option value="pro">Plano Pro</option>
                  <option value="enterprise">Plano Enterprise</option>
                </select>
                <select
                  name="billing_type"
                  className="rounded-xl px-4 py-3 border border-zinc-200 bg-zinc-50 focus:outline-none focus:ring-2 focus:ring-emerald-300"
                  value={checkoutForm.billing_type}
                  onChange={handleCheckoutChange}
                >
                  <option value="PIX">PIX</option>
                  <option value="BOLETO">Boleto</option>
                  <option value="CREDIT_CARD">Cartão</option>
                </select>
              </div>
              <div className="rounded-xl border border-emerald-200 bg-emerald-50 px-4 py-3 text-sm text-emerald-800">
                Valor do plano selecionado: <strong>R$ {selectedPlanValue.toFixed(2)}</strong>
              </div>
            </>
          )}

          {error && <div className="rounded-lg border border-red-200 bg-red-50 p-3 text-sm text-red-700">{error}</div>}
          {mode === "assinatura" && checkout && (
            <div className="rounded-lg border border-cyan-200 bg-cyan-50 p-3 text-sm text-cyan-900">
              <p>
                <strong>Pagamento:</strong> {checkout.pagamentoId}
              </p>
              <p>
                <strong>Status:</strong> {checkout.paymentStatus}
              </p>
              {checkout.paymentLink && (
                <p className="mt-1">
                  <a className="font-semibold underline" href={checkout.paymentLink} target="_blank" rel="noreferrer">
                    Abrir link de pagamento
                  </a>
                </p>
              )}
              {checkout.pixQrCode && (
                <p className="mt-1 break-all">
                  <strong>PIX copia e cola:</strong> {checkout.pixQrCode}
                </p>
              )}
              {checkout.provisioned && (
                <p className="mt-2 font-semibold text-emerald-700">
                  Conta provisionada com sucesso. Faça login para acessar o painel.
                </p>
              )}
            </div>
          )}

          <div className="flex gap-3 justify-between pt-2">
            <Link href="/nutricionista/login" className="rounded-xl px-4 py-2.5 border border-zinc-200 bg-white text-zinc-700 hover:bg-zinc-50 transition-colors">
              Já tenho acesso
            </Link>
            <button
              disabled={loading}
              type="submit"
              className="ml-auto rounded-xl px-5 py-2.5 bg-emerald-600 hover:bg-emerald-700 text-white font-semibold disabled:opacity-60 transition-all hover:-translate-y-0.5"
            >
              {loading ? "Enviando..." : mode === "trial" ? "Solicitar acesso trial" : "Gerar checkout da assinatura"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
