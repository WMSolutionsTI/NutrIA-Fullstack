"use client";

import Link from "next/link";
import React, { useEffect, useState } from "react";
import { uploadArquivo, enviarArquivoIA, getArquivosRepository, getConversasCliente, enviarArquivoRepositoryParaCliente } from "@/lib/api";

interface FileType {
  value: string;
  label: string;
}

export default function ClienteUpload({ params }: { params: { id: string } }) {
  const clienteId = Number(params.id);
  const [arquivo, setArquivo] = useState<File | null>(null);
  const [tipo, setTipo] = useState("imagem");
  const [descricao, setDescricao] = useState("");
  const [status, setStatus] = useState("");
  const [erro, setErro] = useState("");
  const [arquivosRepo, setArquivosRepo] = useState<any[]>([]);

  const tipos: FileType[] = [
    { value: "imagem", label: "Imagem" },
    { value: "pdf", label: "PDF" },
    { value: "video", label: "Vídeo" },
    { value: "documento", label: "Documento" },
  ];

  const handleSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setErro("");
    setStatus("");

    if (!arquivo) {
      setErro("Selecione um arquivo para upload.");
      return;
    }

    try {
      const formData = new FormData();
      formData.append("nome", arquivo.name);
      formData.append("tipo", tipo);
      formData.append("tenant_id", "1");
      formData.append("descricao", descricao);
      formData.append("file", arquivo);

      const resultado = await uploadArquivo(formData);
      setStatus(`Arquivo enviado com sucesso: ${resultado.nome}`);

      if (descricao.trim()) {
        const resposta = await enviarArquivoIA(resultado.id, clienteId, descricao);
        setStatus(`Arquivo registrado e IA gerou sugestão: ${resposta.sugestao_ia}`);
      }

      setArquivo(null);
      setDescricao("");
      await loadArquivosRepo();
    } catch (error) {
      console.error(error);
      setErro("Falha ao enviar arquivo. Verifique a conexão e tente novamente.");
    }
  };

  const loadArquivosRepo = async () => {
    try {
      const repo = await getArquivosRepository(1);
      setArquivosRepo(repo);
    } catch (error) {
      console.error(error);
    }
  };

  useEffect(() => {
    loadArquivosRepo();
  }, []);

  const handleEnviarParaCliente = async (arquivoId: number) => {
    setErro("");
    setStatus("");
    try {
      const conversas = await getConversasCliente(clienteId);
      const conversationId = conversas?.[0]?.id || "";
      const accountId = "1";

      const result = await enviarArquivoRepositoryParaCliente(arquivoId, clienteId, accountId, String(conversationId));
      setStatus(`Arquivo enviado ao cliente. IA: ${result.sugestao_ia}`);
    } catch (error) {
      console.error(error);
      setErro("Falha ao enviar arquivo ao cliente.");
    }
  };

  return (
    <div className="mx-auto w-full max-w-6xl space-y-6">
      <section className="rounded-3xl border border-emerald-100 bg-white p-7 shadow-sm">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div>
            <h1 className="text-3xl font-black text-zinc-900">Upload de Arquivo • Cliente {clienteId}</h1>
            <p className="mt-2 text-zinc-600">
              Envie materiais, registre contexto clínico e acione envio inteligente via IA.
            </p>
          </div>
          <Link href={`/nutricionista/clientes/${clienteId}`} className="rounded-xl border border-zinc-300 bg-white px-4 py-2 text-sm font-semibold text-zinc-700 hover:bg-zinc-50">
            Voltar ao cliente
          </Link>
        </div>
      </section>

      <section className="grid gap-4 lg:grid-cols-[1.1fr_0.9fr]">
        <form onSubmit={handleSubmit} className="rounded-2xl border border-zinc-200 bg-white p-6 shadow-sm">
          <div>
            <label className="block text-sm font-medium text-zinc-700">Arquivo</label>
            <input
              type="file"
              accept="image/*,.pdf,video/*"
              onChange={(e) => setArquivo(e.target.files?.[0] || null)}
              className="mt-1 block w-full rounded-xl border border-zinc-200 bg-zinc-50 px-3 py-2.5 text-sm"
            />
          </div>

          <div className="mt-4">
            <label className="block text-sm font-medium text-zinc-700">Tipo do arquivo</label>
            <select
              value={tipo}
              onChange={(e) => setTipo(e.target.value)}
              className="mt-1 block w-full rounded-xl border border-zinc-200 bg-zinc-50 px-3 py-2.5 text-sm"
            >
              {tipos.map((t) => (
                <option key={t.value} value={t.value}>{t.label}</option>
              ))}
            </select>
          </div>

          <div className="mt-4">
            <label className="block text-sm font-medium text-zinc-700">Descrição/Contexto</label>
            <textarea
              value={descricao}
              onChange={(e) => setDescricao(e.target.value)}
              placeholder="Explique para o agente IA o contexto do arquivo e quando foi criado."
              className="mt-1 block h-32 w-full rounded-xl border border-zinc-200 bg-zinc-50 px-3 py-2.5 text-sm"
              rows={4}
            />
          </div>

          {erro && <div className="mt-4 rounded-xl bg-rose-50 px-3 py-2 text-sm font-semibold text-rose-700">{erro}</div>}
          {status && <div className="mt-4 rounded-xl bg-emerald-50 px-3 py-2 text-sm font-semibold text-emerald-700">{status}</div>}

          <button className="mt-4 rounded-xl bg-emerald-500 px-6 py-2.5 text-sm font-semibold text-white hover:bg-emerald-600">
            Enviar e gerar IA
          </button>
        </form>

        <div className="rounded-2xl border border-zinc-200 bg-white p-6 shadow-sm">
          <h2 className="text-2xl font-bold text-zinc-900">Repositório da nutricionista</h2>
          {arquivosRepo.length === 0 && <p className="mt-2 text-sm text-zinc-500">Nenhum arquivo no repositório.</p>}
          {arquivosRepo.length > 0 && (
            <div className="mt-4 space-y-2">
              {arquivosRepo.map((arquivo) => (
                <div key={arquivo.id} className="flex items-center justify-between rounded-xl border border-zinc-200 bg-zinc-50 p-3">
                  <div>
                    <p className="font-semibold text-zinc-900">{arquivo.nome}</p>
                    <p className="text-xs text-zinc-500">Tipo: {arquivo.tipo} · Tamanho: {arquivo.tamanho || "-"}</p>
                  </div>
                  <button
                    onClick={() => handleEnviarParaCliente(arquivo.id)}
                    className="rounded-xl bg-cyan-600 px-3 py-1.5 text-xs font-semibold text-white hover:bg-cyan-700"
                  >
                    Enviar cópia
                  </button>
                </div>
              ))}
            </div>
          )}
        </div>
      </section>
    </div>
  );
}
