"use client";
import React, { useState } from "react";
import { uploadArquivo, enviarArquivoIA } from "@/lib/api";

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
      formData.append("cliente_id", String(clienteId));
      formData.append("conversa_id", "");
      formData.append("file", arquivo);

      const resultado = await uploadArquivo(formData);
      setStatus(`Arquivo enviado com sucesso: ${resultado.nome}`);

      if (descricao.trim()) {
        const idArquivo = resultado.id;
        const resposta = await enviarArquivoIA(idArquivo, clienteId, descricao);
        setStatus(`Arquivo registrado. IA sugeriu mensagem: ${resposta.sugestao_ia}`);
      }

      setArquivo(null);
      setDescricao("");
    } catch (error) {
      console.error(error);
      setErro("Falha ao enviar arquivo. Verifique a conexão e tente novamente.");
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
      </div>
    </div>
  );
}
