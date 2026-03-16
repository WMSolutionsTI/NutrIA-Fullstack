"""
NutrIA-Pro — Shared Queue Events

Defines the event schemas published by the API to RabbitMQ
and consumed by the Workers. Both services import from here
to ensure consistency.

Usage:
    # In the API (publisher):
    from shared.events import MealPlanGenerationEvent
    await publish(exchange, MealPlanGenerationEvent(...))

    # In the Worker (consumer):
    from shared.events import MealPlanGenerationEvent
    event = MealPlanGenerationEvent.model_validate(message_data)
"""

from enum import StrEnum

from pydantic import BaseModel, Field


class QueueName(StrEnum):
    """Filas RabbitMQ utilizadas pela aplicação."""

    MEAL_PLAN_GENERATION = "queue.mealplan.generation"
    MESSAGING = "queue.messaging"
    HUMAN_ESCALATION = "queue.human_escalation"
    AI_RESUME = "queue.ai_resume"
    CAMPAIGNS = "queue.campaigns"
    NOTIFICATIONS = "queue.notifications"


class ExchangeName(StrEnum):
    """Exchanges RabbitMQ."""

    NUTRIA_PRO = "nutriapro.events"


# ---------------------------------------------------------------------------
# Eventos de Plano Alimentar
# ---------------------------------------------------------------------------


class MealPlanGenerationEvent(BaseModel):
    """
    Publicado pela API quando um nutricionista solicita a geração de um
    plano alimentar. Consumido pelo Worker de geração de planos.
    """

    meal_plan_id: str = Field(..., description="UUID do plano alimentar no PostgreSQL")
    tenant_id: str = Field(..., description="UUID do tenant (clínica)")
    client_id: str = Field(..., description="UUID do cliente/paciente")
    client_name: str = Field(..., description="Nome do paciente")
    dietary_preferences: list[str] = Field(default_factory=list)
    goals: list[str] = Field(default_factory=list)
    restrictions: list[str] = Field(default_factory=list)
    observations: str | None = None


class MealPlanResultEvent(BaseModel):
    """
    Publicado pelo Worker após processar a geração do plano alimentar.
    Consumido pela API para notificar o frontend via SSE.
    """

    meal_plan_id: str
    tenant_id: str
    client_id: str
    success: bool
    error_message: str | None = None


# ---------------------------------------------------------------------------
# Eventos de Mensagens
# ---------------------------------------------------------------------------


class MessagingEvent(BaseModel):
    """