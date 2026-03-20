"use client";
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
    <div className="min-h-screen bg-gradient-to-br from-emerald-100 via-white to-blue-100 dark:from-zinc-900 dark:via-black dark:to-zinc-800 px-4 py-8">
      <div className="max-w-3xl mx-auto bg-white dark:bg-zinc-900 rounded-xl shadow-lg p-8 border border-emerald-100 dark:border-zinc-800">
        <h1 className="text-3xl font-bold text-emerald-700 dark:text-emerald-300 mb-4">Upload de arquivo para cliente {clienteId}</h1>
        <p className="mb-5 text-zinc-600 dark:text-zinc-300">Selecione o arquivo e defina o contexto para que o agente IA sugira e dispare a comunicação ideal.</p>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-zinc-700 dark:text-zinc-100">Arquivo</label>
            <input
              type="file"
              accept="image/*,.pdf,video/*"
              onChange={(e) => setArquivo(e.target.files?.[0] || null)}
              className="mt-1 block w-full rounded border border-zinc-300 dark:border-zinc-700 bg-white dark:bg-zinc-800 px-3 py-2"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-zinc-700 dark:text-zinc-100">Tipo do arquivo</label>
            <select
              value={tipo}
              onChange={(e) => setTipo(e.target.value)}
              className="mt-1 block w-full rounded border border-zinc-300 dark:border-zinc-700 bg-white dark:bg-zinc-800 px-3 py-2"
            >
              {tipos.map((t) => (
                <option key={t.value} value={t.value}>{t.label}</option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-zinc-700 dark:text-zinc-100">Descrição/Contexto</label>
            <textarea
              value={descricao}
              onChange={(e) => setDescricao(e.target.value)}
              placeholder="Explique para o agente IA o contexto do arquivo e quando foi criado."
              className="mt-1 block w-full rounded border border-zinc-300 dark:border-zinc-700 bg-white dark:bg-zinc-800 px-3 py-2"
              rows={4}
            />
          </div>

          {erro && <div className="text-sm text-red-700 dark:text-red-400">{erro}</div>}
          {status && <div className="text-sm text-green-700 dark:text-green-400">{status}</div>}

          <button className="rounded bg-emerald-500 hover:bg-emerald-600 text-white px-6 py-2 font-semibold">Enviar e gerar IA</button>
        </form>

        <div className="mt-8">
          <h2 className="text-2xl font-bold text-emerald-700 dark:text-emerald-300 mb-3">Repositório de arquivos (nutricionista)</h2>
          {arquivosRepo.length === 0 && <p className="text-zinc-600 dark:text-zinc-300">Nenhum arquivo no repositório.</p>}
          {arquivosRepo.length > 0 && (
            <div className="space-y-2">
              {arquivosRepo.map((arquivo) => (
                <div key={arquivo.id} className="flex items-center justify-between rounded border p-3 dark:border-zinc-700">
                  <div>
                    <p className="font-semibold">{arquivo.nome}</p>
                    <p className="text-xs text-zinc-500 dark:text-zinc-400">Tipo: {arquivo.tipo} · Tamanho: {arquivo.tamanho || "-"}</p>
                  </div>
                  <button
                    onClick={() => handleEnviarParaCliente(arquivo.id)}
                    className="rounded bg-blue-500 hover:bg-blue-600 text-white px-3 py-1 text-sm"
                  >
                    Enviar copia ao cliente
                  </button>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
