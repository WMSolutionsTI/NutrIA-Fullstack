from datetime import UTC, datetime
import os
import secrets

from app.workers.admin_monitor_worker import notificar_admins


def gerar_senha_temporaria(length: int = 12) -> str:
    alphabet = "ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz23456789"
    return "".join(secrets.choice(alphabet) for _ in range(length))


def provisionar_conta_chatwoot(nome_nutri: str, tenant_id: int) -> dict[str, str]:
    """
    Provisionamento simplificado para ambiente atual.
    Em produção, deve chamar API do Chatwoot para criar account e usuário.
    """
    instance = os.getenv("CHATWOOT_INSTANCE_DEFAULT", "cw-01")
    account_id = f"cw-{instance}-tenant-{tenant_id}"
    return {"chatwoot_account_id": account_id, "chatwoot_instance": instance}


def enviar_email_boas_vindas_assinatura(
    email: str,
    nome: str,
    senha_temporaria: str,
    plano: str,
    limite_inboxes: int,
) -> dict[str, str]:
    """
    Stub de envio de email transacional.
    """
    assunto = f"Bem-vinda ao NutrIA-Pro ({plano})"
    corpo = (
        f"Olá {nome}, sua assinatura foi confirmada. "
        f"Senha temporária: {senha_temporaria}. "
        f"Limite de inboxes do plano: {limite_inboxes}. "
        "Consulte o manual e finalize onboarding no painel."
    )
    notificar_admins(f"Email de onboarding enviado para {email} às {datetime.now(UTC)}")
    return {"assunto": assunto, "corpo": corpo}


def enviar_email_codigo_validacao_nutri(
    email: str,
    nome: str,
    codigo: str,
) -> dict[str, str]:
    assunto = "Código de validação do contato da nutricionista"
    corpo = (
        f"Olá {nome}, recebemos uma solicitação de vínculo de contato. "
        f"Seu código de confirmação é: {codigo}. "
        "Se não reconhece esta tentativa, ignore este email."
    )
    notificar_admins(f"Código de validação enviado para {email} às {datetime.now(UTC)}")
    return {"assunto": assunto, "corpo": corpo}
