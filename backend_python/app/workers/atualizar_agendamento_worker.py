"""
Worker: Atualizar Agendamento

Nesta versão o worker normaliza payload e retorna um resultado estável para
orquestração externa. A atualização efetiva de agenda depende do módulo de
calendário da aplicação e pode ser conectada aqui depois.
"""

from __future__ import annotations


def atualizar_evento_agenda(id_agenda: int, id_evento: int, titulo: str, descricao: str) -> bool:
    # Placeholder controlado: mantém contrato do worker sem quebrar runtime.
    if not id_agenda or not id_evento:
        return False
    if not titulo:
        return False
    return True


def worker(id_agenda: int, id_evento: int, titulo: str, descricao: str) -> dict:
    sucesso = atualizar_evento_agenda(id_agenda, id_evento, titulo, descricao)
    return {"sucesso": sucesso}


if __name__ == "__main__":
    import json
    import sys

    args = json.loads(sys.stdin.read() or "{}")
    result = worker(
        args.get("id_agenda"),
        args.get("id_evento"),
        args.get("titulo"),
        args.get("descricao"),
    )
    print(result)
