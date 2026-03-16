"""
Worker: Atualizar Agendamento
Atualiza eventos/agendamentos na agenda (Google/local) conforme solicitado.
- Recebe id_agenda, id_evento, título e descrição
- Atualiza evento na agenda
- Integra com Google Calendar API ou agenda local
"""
import os
from app.domain.models.evento import Evento
from app.db.session import SessionLocal

# TODO: Integrar com Google Calendar API

    session = SessionLocal()
    evento = session.query(Evento).filter(Evento.agenda_id==id_agenda, Evento.id==id_evento).first()
    if not evento:
        return False
    evento.summary = titulo
    evento.description = descricao
    session.add(evento)
    session.commit()
    return True

    sucesso = atualizar_evento_agenda(id_agenda, id_evento, titulo, descricao)
    return {"sucesso": sucesso}

if __name__ == "__main__":
    import sys
    import json
    args = json.loads(sys.stdin.read())
    result = worker(
        args.get("id_agenda"),
        args.get("id_evento"),
        args.get("titulo"),
        args.get("descricao")
    )
    print(result)