"use client";

import React, { useState } from "react";

export default function ProntuarioPaciente() {
  const [dados, setDados] = useState({ nome: "", idade: "", sexo: "", contato: "", endereco: "" });
  const [historico, setHistorico] = useState({ doencas: "", cirurgias: "", medicamentos: "", alergias: "" });
  const [preferencias, setPreferencias] = useState({ restricoes: "", intolerancias: "", habitos: "", objetivos: "" });
  const [anamnese, setAnamnese] = useState("");
  const [exames, setExames] = useState("");
  const [evolucao, setEvolucao] = useState("");
  const [anexos, setAnexos] = useState<File[]>([]);
  const [observacoes, setObservacoes] = useState("");

  const handleChange =
    <T extends Record<string, unknown>>(setState: React.Dispatch<React.SetStateAction<T>>) =>
    (e: React.ChangeEvent<HTMLInputElement>) =>
      setState((prev) => ({ ...prev, [e.target.name]: e.target.value }));

  return (
    <div className="mx-auto w-full max-w-6xl space-y-6">
      <section className="rounded-3xl border border-emerald-100 bg-white p-7 shadow-sm">
        <h1 className="text-3xl font-black text-zinc-900">Prontuário do Paciente</h1>
        <p className="mt-2 text-zinc-600">
          Registre histórico clínico, evolução e documentos em um formato único para atendimento de excelência.
        </p>
      </section>

      <section className="rounded-2xl border border-zinc-200 bg-white p-6 shadow-sm">
        <div className="grid gap-4 md:grid-cols-2">
          <input name="nome" value={dados.nome} onChange={handleChange(setDados)} placeholder="Nome" className="rounded-xl border border-zinc-200 bg-zinc-50 px-4 py-2.5 text-sm" />
          <input name="idade" value={dados.idade} onChange={handleChange(setDados)} placeholder="Idade" className="rounded-xl border border-zinc-200 bg-zinc-50 px-4 py-2.5 text-sm" />
          <input name="sexo" value={dados.sexo} onChange={handleChange(setDados)} placeholder="Sexo" className="rounded-xl border border-zinc-200 bg-zinc-50 px-4 py-2.5 text-sm" />
          <input name="contato" value={dados.contato} onChange={handleChange(setDados)} placeholder="Contato" className="rounded-xl border border-zinc-200 bg-zinc-50 px-4 py-2.5 text-sm" />
          <input name="endereco" value={dados.endereco} onChange={handleChange(setDados)} placeholder="Endereço" className="rounded-xl border border-zinc-200 bg-zinc-50 px-4 py-2.5 text-sm md:col-span-2" />
        </div>

        <div className="mt-5 grid gap-4 md:grid-cols-2">
          <input name="doencas" value={historico.doencas} onChange={handleChange(setHistorico)} placeholder="Doenças" className="rounded-xl border border-zinc-200 bg-zinc-50 px-4 py-2.5 text-sm" />
          <input name="cirurgias" value={historico.cirurgias} onChange={handleChange(setHistorico)} placeholder="Cirurgias" className="rounded-xl border border-zinc-200 bg-zinc-50 px-4 py-2.5 text-sm" />
          <input name="medicamentos" value={historico.medicamentos} onChange={handleChange(setHistorico)} placeholder="Medicamentos" className="rounded-xl border border-zinc-200 bg-zinc-50 px-4 py-2.5 text-sm" />
          <input name="alergias" value={historico.alergias} onChange={handleChange(setHistorico)} placeholder="Alergias" className="rounded-xl border border-zinc-200 bg-zinc-50 px-4 py-2.5 text-sm" />
        </div>

        <div className="mt-5 grid gap-4 md:grid-cols-2">
          <input name="restricoes" value={preferencias.restricoes} onChange={handleChange(setPreferencias)} placeholder="Restrições" className="rounded-xl border border-zinc-200 bg-zinc-50 px-4 py-2.5 text-sm" />
          <input name="intolerancias" value={preferencias.intolerancias} onChange={handleChange(setPreferencias)} placeholder="Intolerâncias" className="rounded-xl border border-zinc-200 bg-zinc-50 px-4 py-2.5 text-sm" />
          <input name="habitos" value={preferencias.habitos} onChange={handleChange(setPreferencias)} placeholder="Hábitos" className="rounded-xl border border-zinc-200 bg-zinc-50 px-4 py-2.5 text-sm" />
          <input name="objetivos" value={preferencias.objetivos} onChange={handleChange(setPreferencias)} placeholder="Objetivos" className="rounded-xl border border-zinc-200 bg-zinc-50 px-4 py-2.5 text-sm" />
        </div>

        <div className="mt-5 space-y-4">
          <textarea value={anamnese} onChange={(e) => setAnamnese(e.target.value)} placeholder="Anamnese detalhada" className="h-24 w-full rounded-xl border border-zinc-200 bg-zinc-50 px-4 py-2.5 text-sm" />
          <textarea value={exames} onChange={(e) => setExames(e.target.value)} placeholder="Exames solicitados e status" className="h-20 w-full rounded-xl border border-zinc-200 bg-zinc-50 px-4 py-2.5 text-sm" />
          <textarea value={evolucao} onChange={(e) => setEvolucao(e.target.value)} placeholder="Evolução clínica" className="h-20 w-full rounded-xl border border-zinc-200 bg-zinc-50 px-4 py-2.5 text-sm" />
          <div className="rounded-xl border border-zinc-200 bg-zinc-50 p-4">
            <p className="text-sm font-semibold text-zinc-700">Arquivos anexos</p>
            <input
              type="file"
              multiple
              onChange={(e) => setAnexos([...anexos, ...Array.from(e.target.files || [])])}
              className="mt-2 block w-full text-sm"
            />
            {anexos.length > 0 && (
              <ul className="mt-3 space-y-1 text-sm text-zinc-600">
                {anexos.map((file, idx) => (
                  <li key={`${file.name}-${idx}`}>{file.name}</li>
                ))}
              </ul>
            )}
          </div>
          <textarea value={observacoes} onChange={(e) => setObservacoes(e.target.value)} placeholder="Observações do nutricionista" className="h-20 w-full rounded-xl border border-zinc-200 bg-zinc-50 px-4 py-2.5 text-sm" />
        </div>
      </section>
    </div>
  );
}
