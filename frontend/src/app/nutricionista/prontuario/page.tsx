import React, { useState } from "react";

export default function ProntuarioPaciente() {
  // Estados para os campos principais
  const [dados, setDados] = useState({ nome: "", idade: "", sexo: "", contato: "", endereco: "" });
  const [historico, setHistorico] = useState({ doencas: "", cirurgias: "", medicamentos: "", alergias: "" });
  const [preferencias, setPreferencias] = useState({ restricoes: "", intolerancias: "", habitos: "", objetivos: "" });
  const [anamnese, setAnamnese] = useState("");
  const [exames, setExames] = useState("");
  const [evolucao, setEvolucao] = useState("");
  const [anexos, setAnexos] = useState([]);
  const [observacoes, setObservacoes] = useState("");

  // Handlers genéricos
  const handleChange = (setState) => (e) => setState(prev => ({ ...prev, [e.target.name]: e.target.value }));

  return (
    <div className="min-h-screen bg-gradient-to-br from-emerald-100 via-white to-blue-100 dark:from-zinc-900 dark:via-black dark:to-zinc-800 px-4 py-8">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-3xl font-bold text-emerald-700 dark:text-emerald-300 mb-8">Prontuário do Paciente</h1>
        {/* Dados Pessoais */}
        <section className="mb-6">
          <h2 className="text-xl font-semibold mb-2">Dados Pessoais</h2>
          <div className="grid grid-cols-2 gap-4">
            <input name="nome" value={dados.nome} onChange={handleChange(setDados)} placeholder="Nome" className="input" />
            <input name="idade" value={dados.idade} onChange={handleChange(setDados)} placeholder="Idade" className="input" />
            <input name="sexo" value={dados.sexo} onChange={handleChange(setDados)} placeholder="Sexo" className="input" />
            <input name="contato" value={dados.contato} onChange={handleChange(setDados)} placeholder="Contato" className="input" />
            <input name="endereco" value={dados.endereco} onChange={handleChange(setDados)} placeholder="Endereço" className="input col-span-2" />
          </div>
        </section>
        {/* Histórico Médico */}
        <section className="mb-6">
          <h2 className="text-xl font-semibold mb-2">Histórico Médico</h2>
          <div className="grid grid-cols-2 gap-4">
            <input name="doencas" value={historico.doencas} onChange={handleChange(setHistorico)} placeholder="Doenças" className="input" />
            <input name="cirurgias" value={historico.cirurgias} onChange={handleChange(setHistorico)} placeholder="Cirurgias" className="input" />
            <input name="medicamentos" value={historico.medicamentos} onChange={handleChange(setHistorico)} placeholder="Medicamentos" className="input" />
            <input name="alergias" value={historico.alergias} onChange={handleChange(setHistorico)} placeholder="Alergias" className="input" />
          </div>
        </section>
        {/* Preferências Alimentares */}
        <section className="mb-6">
          <h2 className="text-xl font-semibold mb-2">Preferências Alimentares</h2>
          <div className="grid grid-cols-2 gap-4">
            <input name="restricoes" value={preferencias.restricoes} onChange={handleChange(setPreferencias)} placeholder="Restrições" className="input" />
            <input name="intolerancias" value={preferencias.intolerancias} onChange={handleChange(setPreferencias)} placeholder="Intolerâncias" className="input" />
            <input name="habitos" value={preferencias.habitos} onChange={handleChange(setPreferencias)} placeholder="Hábitos" className="input" />
            <input name="objetivos" value={preferencias.objetivos} onChange={handleChange(setPreferencias)} placeholder="Objetivos" className="input" />
          </div>
        </section>
        {/* Anamnese */}
        <section className="mb-6">
          <h2 className="text-xl font-semibold mb-2">Anamnese</h2>
          <textarea value={anamnese} onChange={e => setAnamnese(e.target.value)} placeholder="Anamnese detalhada" className="input w-full h-24" />
        </section>
        {/* Solicitação de Exames */}
        <section className="mb-6">
          <h2 className="text-xl font-semibold mb-2">Solicitação de Exames</h2>
          <textarea value={exames} onChange={e => setExames(e.target.value)} placeholder="Exames solicitados e status" className="input w-full h-16" />
        </section>
        {/* Evolução */}
        <section className="mb-6">
          <h2 className="text-xl font-semibold mb-2">Evolução</h2>
          <textarea value={evolucao} onChange={e => setEvolucao(e.target.value)} placeholder="Registros de consultas, metas, progresso" className="input w-full h-16" />
        </section>
        {/* Arquivos Anexos */}
        <section className="mb-6">
          <h2 className="text-xl font-semibold mb-2">Arquivos Anexos</h2>
          <input type="file" multiple onChange={e => setAnexos([...anexos, ...Array.from(e.target.files || [])])} className="input" />
          <ul className="mt-2">
            {anexos.map((file, idx) => (
              <li key={idx}>{file.name}</li>
            ))}
          </ul>
        </section>
        {/* Observações */}
        <section className="mb-6">
          <h2 className="text-xl font-semibold mb-2">Observações</h2>
          <textarea value={observacoes} onChange={e => setObservacoes(e.target.value)} placeholder="Notas do nutricionista" className="input w-full h-16" />
        </section>
      </div>
    </div>
  );
}

// Estilos básicos para inputs
// Adicione ao seu CSS global:
// .input { border-radius: 0.5rem; border: 1px solid #d1d5db; padding: 0.5rem; background: #fff; color: #222; }
// .input:focus { outline: none; border-color: #10b981; background: #f0fdf4; }