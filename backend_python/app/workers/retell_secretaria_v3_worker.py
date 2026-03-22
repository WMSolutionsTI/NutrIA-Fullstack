"""
Worker: Retell - Secretária v3

Implementação mínima estável para orquestrar chamadas de voz sem dependências
internas ausentes. Mantém contrato de entrada/saída para futura integração.
"""

from __future__ import annotations

from typing import Any


def gerar_resposta_voz(prompt: str, contexto: dict[str, Any]) -> str:
    historico = contexto.get("historico")
    if historico:
        return "Continuando atendimento com base no histórico da cliente."
    return f"Atendimento iniciado: {prompt}"


def worker(payload: dict[str, Any]) -> dict[str, Any]:
    contato_id = payload.get("contato_id")
    call_direction = payload.get("call_direction", "inbound")
    finalizar = bool(payload.get("finalizar"))

    contexto: dict[str, Any] = {}
    if call_direction == "outbound":
        contexto["historico"] = "outbound_followup"

    resposta = gerar_resposta_voz("fluxo-inicial", contexto)
    return {
        "status": "ok",
        "contato_id": contato_id,
        "call_direction": call_direction,
        "resposta": resposta,
        "chamada_finalizada": finalizar,
    }


if __name__ == "__main__":
    import json
    import sys

    payload = json.loads(sys.stdin.read() or "{}")
    print(worker(payload))
