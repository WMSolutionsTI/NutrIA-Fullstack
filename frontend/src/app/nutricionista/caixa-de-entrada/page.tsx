"use client";

import Link from "next/link";
import { FormEvent, useEffect, useMemo, useRef, useState } from "react";

import { criarConversa, getClientes, getConversasCliente } from "@/lib/api";
import { ApiError } from "@/lib/api/client";
import { Inbox, listInboxes } from "@/lib/api/inboxes";
import { listVoiceHandoffs } from "@/lib/api/voz";

type Contato = {
  id: string;
  nome: string;
  email?: string;
  telefone?: string;
  status?: string;
};

type ChatMensagem = {
  id: string;
  autor: "cliente" | "nutricionista";
  conteudo: string;
  data: string;
  tipo: "texto" | "arquivo" | "midia";
};

type AlertaAtendimento = {
  id: string;
  contatoId: string;
  contatoNome: string;
  motivo: string;
  quando: string;
  conversaLink: string;
};

const FRASES_SOLICITAR_NUTRI = [
  "falar com a nutricionista",
  "falar com nutricionista",
  "quero falar com a nutri",
  "quero falar com a nutricionista",
];

const ALERTAS_ENVIADOS_KEY = "nutria-pro:alertas_cliente_pediu_nutri";

function normalizarTexto(value: string) {
  return value.toLowerCase().normalize("NFD").replace(/\p{Diacritic}/gu, "");
}

function detectouPedidoNutri(msgs: ChatMensagem[]) {
  return msgs.some((msg) => {
    if (msg.autor !== "cliente") return false;
    const base = normalizarTexto(msg.conteudo);
    return FRASES_SOLICITAR_NUTRI.some((frase) => base.includes(normalizarTexto(frase)));
  });
}

function readAlertasEnviados(): Record<string, string> {
  if (typeof window === "undefined") return {};
  try {
    const raw = localStorage.getItem(ALERTAS_ENVIADOS_KEY);
    if (!raw) return {};
    return JSON.parse(raw) as Record<string, string>;
  } catch {
    return {};
  }
}

function writeAlertasEnviados(data: Record<string, string>) {
  if (typeof window === "undefined") return;
  localStorage.setItem(ALERTAS_ENVIADOS_KEY, JSON.stringify(data));
}

export default function CaixaDeEntradaPage() {
  const [inboxes, setInboxes] = useState<Inbox[]>([]);
  const [loadingInboxes, setLoadingInboxes] = useState(true);
  const [selectedInboxId, setSelectedInboxId] = useState<number | null>(null);

  const [contatos, setContatos] = useState<Contato[]>([]);
  const [loadingContatos, setLoadingContatos] = useState(true);
  const [selectedContatoId, setSelectedContatoId] = useState<string | null>(null);
  const [buscaContato, setBuscaContato] = useState("");

  const [mensagens, setMensagens] = useState<Record<string, ChatMensagem[]>>({});
  const [loadingMensagens, setLoadingMensagens] = useState(false);

  const [novaMensagem, setNovaMensagem] = useState("");
  const [anexo, setAnexo] = useState<File | null>(null);
  const [erro, setErro] = useState("");
  const [sucesso, setSucesso] = useState("");

  const [secretariaAtivaPorConversa, setSecretariaAtivaPorConversa] = useState<Record<string, boolean>>({});
  const [alertas, setAlertas] = useState<AlertaAtendimento[]>([]);
  const timersReativacaoRef = useRef<Record<string, ReturnType<typeof setTimeout>>>({});
  const alertasEnviadosRef = useRef<Record<string, string>>({});

  const selectedInbox = useMemo(
    () => inboxes.find((item) => item.id === selectedInboxId) ?? null,
    [inboxes, selectedInboxId]
  );
  const selectedContato = useMemo(
    () => contatos.find((item) => item.id === selectedContatoId) ?? null,
    [contatos, selectedContatoId]
  );

  const conversaKey = useMemo(() => {
    if (!selectedInboxId || !selectedContatoId) return null;
    return `${selectedInboxId}:${selectedContatoId}`;
  }, [selectedInboxId, selectedContatoId]);

  const mensagensAtuais = conversaKey ? mensagens[conversaKey] ?? [] : [];
  const secretariaAtiva = conversaKey ? secretariaAtivaPorConversa[conversaKey] ?? true : true;

  const contatosFiltrados = useMemo(() => {
    const termo = buscaContato.trim().toLowerCase();
    if (!termo) return contatos;
    return contatos.filter((c) => c.nome.toLowerCase().includes(termo));
  }, [contatos, buscaContato]);

  async function carregarInboxes() {
    setLoadingInboxes(true);
    try {
      const data = await listInboxes();
      setInboxes(data);
      if (!selectedInboxId && data.length > 0) {
        setSelectedInboxId(data[0].id);
      }
    } catch (e) {
      const detail = e instanceof ApiError ? e.detail : "Falha ao carregar inboxes.";
      setErro(detail);
    } finally {
      setLoadingInboxes(false);
    }
  }

  async function carregarContatos() {
    setLoadingContatos(true);
    try {
      const data = await getClientes();
      const lista = (Array.isArray(data) ? data : []).map((item: any) => ({
        id: String(item.id),
        nome: item.nome ?? `Contato #${item.id}`,
        email: item.email,
        telefone: item.telefone ?? item.contato_chatwoot,
        status: item.status,
      }));
      setContatos(lista);
      if (!selectedContatoId && lista.length > 0) {
        setSelectedContatoId(lista[0].id);
      }
    } catch {
      setErro("Falha ao carregar contatos.");
    } finally {
      setLoadingContatos(false);
    }
  }

  async function carregarAlertasVoice() {
    try {
      const items = await listVoiceHandoffs(20);
      const fromVoice: AlertaAtendimento[] = (Array.isArray(items) ? items : []).map((item) => ({
        id: `voice-${item.call_id}`,
        contatoId: String(item.cliente_id),
        contatoNome: item.cliente_nome ?? `Cliente #${item.cliente_id}`,
        motivo: `Fallback de voz (${item.status}): ${item.motivo}`,
        quando: item.quando ?? new Date().toISOString(),
        conversaLink: item.conversa_link,
      }));
      setAlertas((prev) => {
        const local = prev.filter((alerta) => !alerta.id.startsWith("voice-"));
        return [...fromVoice, ...local].slice(0, 20);
      });
    } catch {
      // alerta de voz é complementar; não bloqueia a tela
    }
  }

  function agendarReativacaoAutomatica(key: string) {
    const anterior = timersReativacaoRef.current[key];
    if (anterior) clearTimeout(anterior);
    timersReativacaoRef.current[key] = setTimeout(() => {
      setSecretariaAtivaPorConversa((prev) => ({ ...prev, [key]: true }));
      setSucesso("Secretária reativada automaticamente após 5 minutos sem interação.");
    }, 5 * 60 * 1000);
  }

  function findContatoNutri() {
    return contatos.find((contato) => {
      const status = (contato.status ?? "").toLowerCase();
      return (
        status === "nutri" ||
        status === "cliente_nutri" ||
        status === "contato_nutri" ||
        status === "em_atendimento_direto"
      );
    });
  }

  async function encaminharAlertaParaContatoNutri(
    contatoSolicitante: Contato,
    triggerMsgId: string
  ) {
    if (!selectedInboxId) return;
    const contatoNutri = findContatoNutri();
    if (!contatoNutri) return;

    const alertaKey = `${selectedInboxId}:${contatoSolicitante.id}`;
    const ultimoTriggerEnviado = alertasEnviadosRef.current[alertaKey];
    if (ultimoTriggerEnviado === triggerMsgId) return;

    const conversaPath = `/nutricionista/caixa-de-entrada?inbox=${selectedInboxId}&contato=${contatoSolicitante.id}`;
    const conversaLink = typeof window !== "undefined" ? `${window.location.origin}${conversaPath}` : conversaPath;
    const mensagemAlerta =
      `ALERTA: ${contatoSolicitante.nome} solicitou falar com a nutricionista. ` +
      `Acesse a conversa: ${conversaLink}`;

    try {
      await criarConversa({
        cliente_id: Number(contatoNutri.id),
        nutricionista_id: 1,
        caixa_id: selectedInboxId,
        mensagem: mensagemAlerta,
        modo: "ia",
      });

      alertasEnviadosRef.current = {
        ...alertasEnviadosRef.current,
        [alertaKey]: triggerMsgId,
      };
      writeAlertasEnviados(alertasEnviadosRef.current);

      setAlertas((prev) => [
        {
          id: `local-${contatoSolicitante.id}-${Date.now()}`,
          contatoId: contatoSolicitante.id,
          contatoNome: contatoSolicitante.nome,
          motivo: "Cliente solicitou falar diretamente com a nutricionista.",
          quando: new Date().toISOString(),
          conversaLink: conversaPath,
        },
        ...prev,
      ]);

      setSucesso(
        "Alerta encaminhado para o contato da nutricionista com link direto da conversa."
      );
    } catch {
      setErro("Falha ao encaminhar alerta para o contato da nutricionista.");
    }
  }

  function desativarPorSolicitacaoDoCliente(
    key: string,
    contato: Contato,
    triggerMsgId: string
  ) {
    setSecretariaAtivaPorConversa((prev) => ({ ...prev, [key]: false }));
    encaminharAlertaParaContatoNutri(contato, triggerMsgId);
  }

  async function carregarMensagensContato(contatoId: string) {
    if (!selectedInboxId) return;
    const key = `${selectedInboxId}:${contatoId}`;
    setLoadingMensagens(true);
    try {
      const conversa = await getConversasCliente(Number(contatoId));
      const mapped: ChatMensagem[] = (Array.isArray(conversa) ? conversa : []).map((c: any) => ({
        id: String(c.id),
        autor: c.autor === "nutricionista" ? "nutricionista" : "cliente",
        conteudo: c.mensagem ?? "",
        data: c.data ?? new Date().toISOString(),
        tipo: "texto",
      }));

      setMensagens((prev) => ({ ...prev, [key]: mapped }));
      setSecretariaAtivaPorConversa((prev) => {
        if (prev[key] !== undefined) return prev;
        return { ...prev, [key]: true };
      });

      const contato = contatos.find((item) => item.id === contatoId);
      if (contato && detectouPedidoNutri(mapped)) {
        const trigger = [...mapped]
          .reverse()
          .find(
            (msg) =>
              msg.autor === "cliente" &&
              FRASES_SOLICITAR_NUTRI.some((frase) =>
                normalizarTexto(msg.conteudo).includes(normalizarTexto(frase))
              )
          );
        if (trigger) {
          desativarPorSolicitacaoDoCliente(key, contato, trigger.id);
        }
      }
    } catch {
      setErro("Falha ao carregar conversa do contato selecionado.");
    } finally {
      setLoadingMensagens(false);
    }
  }

  useEffect(() => {
    alertasEnviadosRef.current = readAlertasEnviados();
    carregarInboxes();
    carregarContatos();
    carregarAlertasVoice();
    return () => {
      Object.values(timersReativacaoRef.current).forEach((timer) => clearTimeout(timer));
      timersReativacaoRef.current = {};
    };
  }, []);

  useEffect(() => {
    if (typeof window === "undefined") return;
    const params = new URLSearchParams(window.location.search);
    const contato = params.get("contato");
    const inbox = params.get("inbox");
    if (inbox) {
      const parsedInbox = Number(inbox);
      if (!Number.isNaN(parsedInbox)) {
        setSelectedInboxId(parsedInbox);
      }
    }
    if (contato) {
      setSelectedContatoId(contato);
    }
  }, []);

  useEffect(() => {
    if (!selectedContatoId) return;
    carregarMensagensContato(selectedContatoId);
  }, [selectedInboxId, selectedContatoId]);

  async function handleEnviarMensagem(event: FormEvent) {
    event.preventDefault();
    setErro("");
    setSucesso("");
    if (!selectedContato || !selectedInbox) {
      setErro("Selecione inbox e contato para enviar mensagem.");
      return;
    }
    if (!novaMensagem.trim() && !anexo) {
      setErro("Digite uma mensagem ou selecione um arquivo/mídia.");
      return;
    }

    const key = `${selectedInbox.id}:${selectedContato.id}`;
    const mensagemFormatada = novaMensagem.trim() || `[Arquivo enviado: ${anexo?.name}]`;
    try {
      await criarConversa({
        cliente_id: Number(selectedContato.id),
        nutricionista_id: 1,
        caixa_id: selectedInbox.id,
        mensagem: mensagemFormatada,
        modo: "direto",
      });

      const nova: ChatMensagem = {
        id: `local-${Date.now()}`,
        autor: "nutricionista",
        conteudo: mensagemFormatada,
        data: new Date().toISOString(),
        tipo: anexo ? "arquivo" : "texto",
      };
      setMensagens((prev) => ({ ...prev, [key]: [...(prev[key] ?? []), nova] }));
      setNovaMensagem("");
      setAnexo(null);

      setSecretariaAtivaPorConversa((prev) => ({ ...prev, [key]: false }));
      agendarReativacaoAutomatica(key);
      setSucesso("Mensagem enviada. Secretária desativada temporariamente por 5 minutos.");
    } catch {
      setErro("Não foi possível enviar a mensagem.");
    }
  }

  function toggleSecretaria() {
    if (!conversaKey) return;
    setSecretariaAtivaPorConversa((prev) => {
      const novoEstado = !(prev[conversaKey] ?? true);
      if (novoEstado) {
        const timer = timersReativacaoRef.current[conversaKey];
        if (timer) {
          clearTimeout(timer);
          delete timersReativacaoRef.current[conversaKey];
        }
      } else {
        agendarReativacaoAutomatica(conversaKey);
      }
      return { ...prev, [conversaKey]: novoEstado };
    });
  }

  return (
    <div className="mx-auto w-full max-w-[1500px] space-y-4">
      <section className="rounded-2xl border border-zinc-200 bg-white p-4 shadow-sm">
        <h1 className="text-2xl font-black text-zinc-900">Caixa de Entrada</h1>
        <p className="text-sm text-zinc-600">Atendimento em tempo real com fluxo operacional no estilo WhatsApp.</p>

        <div className="mt-4 flex flex-wrap gap-2">
          {loadingInboxes && <span className="text-sm text-zinc-500">Carregando inboxes...</span>}
          {!loadingInboxes && inboxes.length === 0 && (
            <span className="text-sm text-zinc-500">Sem inboxes ativas. Configure uma inbox para iniciar.</span>
          )}
          {inboxes.map((inbox) => {
            const ativo = inbox.id === selectedInboxId;
            return (
              <button
                key={inbox.id}
                onClick={() => setSelectedInboxId(inbox.id)}
                className={`rounded-xl px-4 py-2 text-sm font-semibold transition ${
                  ativo ? "bg-emerald-500 text-white" : "border border-zinc-300 bg-white text-zinc-700 hover:bg-zinc-50"
                }`}
              >
                {inbox.tipo.toUpperCase()}
              </button>
            );
          })}
          <Link href="/nutricionista/configuracoes" className="ml-auto rounded-xl border border-zinc-300 bg-white px-4 py-2 text-sm font-semibold text-zinc-700 hover:bg-zinc-50">
            Configurações
          </Link>
        </div>
      </section>

      {erro && <div className="rounded-lg border border-red-200 bg-red-50 p-3 text-sm text-red-700">{erro}</div>}
      {sucesso && <div className="rounded-lg border border-emerald-200 bg-emerald-50 p-3 text-sm text-emerald-700">{sucesso}</div>}

      <section className="grid min-h-[72vh] grid-cols-1 gap-4 lg:grid-cols-[320px_1fr_320px]">
        <aside className="rounded-2xl border border-zinc-200 bg-white p-3 shadow-sm">
          <input
            type="text"
            value={buscaContato}
            onChange={(e) => setBuscaContato(e.target.value)}
            placeholder="Buscar contato"
            className="w-full rounded-xl border border-zinc-200 bg-zinc-50 px-3 py-2 text-sm"
          />
          <div className="mt-3 h-[60vh] overflow-y-auto">
            {loadingContatos && <p className="px-2 py-2 text-sm text-zinc-500">Carregando contatos...</p>}
            {!loadingContatos && contatosFiltrados.length === 0 && (
              <p className="px-2 py-2 text-sm text-zinc-500">Nenhum contato encontrado.</p>
            )}
            {contatosFiltrados.map((contato) => {
              const ativo = contato.id === selectedContatoId;
              return (
                <button
                  key={contato.id}
                  onClick={() => setSelectedContatoId(contato.id)}
                  className={`mb-1 w-full rounded-xl px-3 py-2 text-left ${
                    ativo ? "bg-emerald-100" : "hover:bg-zinc-50"
                  }`}
                >
                  <p className="font-semibold text-zinc-900">{contato.nome}</p>
                  <p className="text-xs text-zinc-500">{contato.telefone ?? contato.email ?? "Sem contato"}</p>
                </button>
              );
            })}
          </div>
        </aside>

        <main className="flex min-h-[72vh] flex-col rounded-2xl border border-zinc-200 bg-white shadow-sm">
          <div className="border-b border-zinc-200 px-4 py-3">
            <p className="font-semibold text-zinc-900">
              {selectedContato ? `Conversa com ${selectedContato.nome}` : "Selecione um contato"}
            </p>
            <p className="text-xs text-zinc-500">
              Inbox: {selectedInbox?.tipo.toUpperCase() ?? "-"} • {selectedContato?.telefone ?? selectedContato?.email ?? ""}
            </p>
          </div>

          <div className="flex-1 space-y-2 overflow-y-auto bg-zinc-50 px-4 py-4">
            {loadingMensagens && <p className="text-sm text-zinc-500">Carregando mensagens...</p>}
            {!loadingMensagens && mensagensAtuais.length === 0 && (
              <p className="text-sm text-zinc-500">Sem mensagens para este contato.</p>
            )}
            {mensagensAtuais.map((msg) => (
              <div key={msg.id} className={`flex ${msg.autor === "nutricionista" ? "justify-end" : "justify-start"}`}>
                <div
                  className={`max-w-[78%] rounded-2xl px-4 py-2 text-sm shadow ${
                    msg.autor === "nutricionista"
                      ? "bg-emerald-500 text-white"
                      : "border border-zinc-200 bg-white text-zinc-800"
                  }`}
                >
                  <p>{msg.conteudo}</p>
                  <p className={`mt-1 text-[11px] ${msg.autor === "nutricionista" ? "text-emerald-100" : "text-zinc-500"}`}>
                    {new Date(msg.data).toLocaleTimeString()}
                  </p>
                </div>
              </div>
            ))}
          </div>

          <form onSubmit={handleEnviarMensagem} className="border-t border-zinc-200 p-3">
            <div className="flex items-center gap-2">
              <label className="rounded-xl border border-zinc-300 bg-white px-3 py-2 text-xs font-semibold text-zinc-700 hover:bg-zinc-50 cursor-pointer">
                Arquivo
                <input
                  type="file"
                  className="hidden"
                  onChange={(e) => setAnexo(e.target.files?.[0] ?? null)}
                />
              </label>
              <label className="rounded-xl border border-zinc-300 bg-white px-3 py-2 text-xs font-semibold text-zinc-700 hover:bg-zinc-50 cursor-pointer">
                Mídia
                <input
                  type="file"
                  accept="image/*,video/*,audio/*"
                  className="hidden"
                  onChange={(e) => setAnexo(e.target.files?.[0] ?? null)}
                />
              </label>
              <input
                type="text"
                value={novaMensagem}
                onChange={(e) => setNovaMensagem(e.target.value)}
                placeholder="Digite sua mensagem..."
                className="flex-1 rounded-xl border border-zinc-200 bg-zinc-50 px-4 py-2.5 text-sm"
              />
              <button
                type="submit"
                className="rounded-xl bg-emerald-600 px-4 py-2.5 text-sm font-semibold text-white hover:bg-emerald-700"
              >
                Enviar
              </button>
            </div>
            {anexo && <p className="mt-2 text-xs text-zinc-500">Anexo selecionado: {anexo.name}</p>}
          </form>
        </main>

        <aside className="rounded-2xl border border-zinc-200 bg-white p-4 shadow-sm">
          <h3 className="text-lg font-bold text-zinc-900">Status da conversa</h3>
          <div className="mt-3 flex items-center justify-between rounded-xl border border-zinc-200 bg-zinc-50 p-3">
            <div>
              <p className="text-sm font-semibold text-zinc-800">
                Secretária {secretariaAtiva ? "ativada" : "desativada"}
              </p>
              <p className="text-xs text-zinc-500">
                Desativa ao falar como nutri e reativa em 5 minutos sem interação.
              </p>
            </div>
            <button
              type="button"
              onClick={toggleSecretaria}
              disabled={!conversaKey}
              className={`h-7 w-12 rounded-full p-1 transition ${
                secretariaAtiva ? "bg-emerald-500" : "bg-zinc-300"
              }`}
            >
              <span
                className={`block h-5 w-5 rounded-full bg-white transition ${
                  secretariaAtiva ? "translate-x-5" : "translate-x-0"
                }`}
              />
            </button>
          </div>

          <div className="mt-5">
            <h4 className="text-sm font-semibold text-zinc-700">Detalhes do cliente</h4>
            {!selectedContato && <p className="mt-2 text-sm text-zinc-500">Selecione um contato.</p>}
            {selectedContato && (
              <div className="mt-2 space-y-1 text-sm text-zinc-700">
                <p><strong>Nome:</strong> {selectedContato.nome}</p>
                <p><strong>Telefone:</strong> {selectedContato.telefone ?? "-"}</p>
                <p><strong>E-mail:</strong> {selectedContato.email ?? "-"}</p>
                <p><strong>Status:</strong> {selectedContato.status ?? "-"}</p>
              </div>
            )}
          </div>

          <div className="mt-5">
            <h4 className="text-sm font-semibold text-zinc-700">Alertas para nutricionista</h4>
            {alertas.length === 0 && <p className="mt-2 text-sm text-zinc-500">Sem alertas no momento.</p>}
            <div className="mt-2 space-y-2">
              {alertas.slice(0, 5).map((alerta) => (
                <div key={alerta.id} className="rounded-xl border border-amber-200 bg-amber-50 p-3">
                  <p className="text-xs font-semibold text-amber-800">{alerta.contatoNome}</p>
                  <p className="text-xs text-amber-700">{alerta.motivo}</p>
                  <p className="mt-1 text-[11px] text-amber-600">{new Date(alerta.quando).toLocaleString()}</p>
                  <Link
                    href={alerta.conversaLink}
                    className="mt-2 inline-block text-[11px] font-semibold text-amber-800 underline"
                  >
                    Abrir conversa
                  </Link>
                </div>
              ))}
            </div>
          </div>
        </aside>
      </section>
    </div>
  );
}
