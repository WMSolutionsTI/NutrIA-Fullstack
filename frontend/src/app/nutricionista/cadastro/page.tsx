"use client";
import React, { useState } from "react";

export default function NutriCadastro() {
  const [step, setStep] = useState(1);
  const [form, setForm] = useState({
    nome: "",
    email: "",
    senha: "",
    telefone: "",
    especialidade: "",
    clinica: "",
    cnpj: "",
    prompt: "",
    horario: "",
    mensagemBoasVindas: "",
  });
  const [error, setError] = useState("");

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const handleNext = () => {
    // Validação simples por etapa
    if (step === 1 && (!form.nome || !form.email || !form.senha)) {
      setError("Preencha nome, e-mail e senha.");
      return;
    }
    if (step === 2 && (!form.telefone || !form.especialidade)) {
      setError("Preencha telefone e especialidade.");
      return;
    }
    setError("");
    setStep(step + 1);
  };

  const handlePrev = () => setStep(step - 1);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    // TODO: Chamada real de API para cadastro
    alert("Cadastro simulado! Dados enviados: " + JSON.stringify(form, null, 2));
  };

  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-gradient-to-br from-emerald-100 via-white to-blue-100 dark:from-zinc-900 dark:via-black dark:to-zinc-800 px-4 py-12">
      <form onSubmit={handleSubmit} className="bg-white dark:bg-zinc-900 rounded-xl shadow-lg p-8 w-full max-w-lg flex flex-col gap-6 border border-emerald-100 dark:border-zinc-800">
        <h1 className="text-3xl font-bold text-center text-emerald-700 dark:text-emerald-300 mb-2">Cadastro de Nutricionista</h1>
        {step === 1 && (
          <>
            <input name="nome" type="text" placeholder="Nome completo" className="rounded px-4 py-3 border border-zinc-200 dark:border-zinc-700 bg-zinc-50 dark:bg-zinc-800" value={form.nome} onChange={handleChange} />
            <input name="email" type="email" placeholder="E-mail" className="rounded px-4 py-3 border border-zinc-200 dark:border-zinc-700 bg-zinc-50 dark:bg-zinc-800" value={form.email} onChange={handleChange} />
            <input name="senha" type="password" placeholder="Senha" className="rounded px-4 py-3 border border-zinc-200 dark:border-zinc-700 bg-zinc-50 dark:bg-zinc-800" value={form.senha} onChange={handleChange} />
          </>
        )}
        {step === 2 && (
          <>
            <input name="telefone" type="tel" placeholder="Telefone" className="rounded px-4 py-3 border border-zinc-200 dark:border-zinc-700 bg-zinc-50 dark:bg-zinc-800" value={form.telefone} onChange={handleChange} />
            <input name="especialidade" type="text" placeholder="Especialidade" className="rounded px-4 py-3 border border-zinc-200 dark:border-zinc-700 bg-zinc-50 dark:bg-zinc-800" value={form.especialidade} onChange={handleChange} />
            <input name="clinica" type="text" placeholder="Nome da clínica (opcional)" className="rounded px-4 py-3 border border-zinc-200 dark:border-zinc-700 bg-zinc-50 dark:bg-zinc-800" value={form.clinica} onChange={handleChange} />
            <input name="cnpj" type="text" placeholder="CNPJ (opcional)" className="rounded px-4 py-3 border border-zinc-200 dark:border-zinc-700 bg-zinc-50 dark:bg-zinc-800" value={form.cnpj} onChange={handleChange} />
          </>
        )}
        {step === 3 && (
          <>
            <textarea name="prompt" placeholder="Prompt/contexto da secretária virtual (ex: especialidade, tom de voz, informações da clínica)" className="rounded px-4 py-3 border border-zinc-200 dark:border-zinc-700 bg-zinc-50 dark:bg-zinc-800" value={form.prompt} onChange={handleChange} />
            <input name="horario" type="text" placeholder="Horário de atendimento (ex: 8h-18h)" className="rounded px-4 py-3 border border-zinc-200 dark:border-zinc-700 bg-zinc-50 dark:bg-zinc-800" value={form.horario} onChange={handleChange} />
            <input name="mensagemBoasVindas" type="text" placeholder="Mensagem de boas-vindas" className="rounded px-4 py-3 border border-zinc-200 dark:border-zinc-700 bg-zinc-50 dark:bg-zinc-800" value={form.mensagemBoasVindas} onChange={handleChange} />
          </>
        )}
        {error && <div className="text-red-600 text-sm text-center">{error}</div>}
        <div className="flex gap-4 justify-between mt-2">
          {step > 1 && <button type="button" onClick={handlePrev} className="rounded bg-zinc-200 dark:bg-zinc-700 text-zinc-700 dark:text-zinc-200 px-4 py-2">Voltar</button>}
          {step < 3 && <button type="button" onClick={handleNext} className="rounded-full bg-emerald-500 hover:bg-emerald-600 text-white px-6 py-3 font-semibold shadow transition-colors ml-auto">Próximo</button>}
          {step === 3 && <button type="submit" className="rounded-full bg-emerald-500 hover:bg-emerald-600 text-white px-6 py-3 font-semibold shadow transition-colors ml-auto">Finalizar cadastro</button>}
        </div>
      </form>
    </div>
  );
}
