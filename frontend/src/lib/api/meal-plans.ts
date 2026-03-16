/**
 * NutrIA-Pro — Meal Plans API
 *
 * Funções para criação e consulta de planos alimentares.
 * O frontend chama a API, que valida, persiste no PostgreSQL
 * e publica uma tarefa no RabbitMQ para o worker processar.
 *
 * Fluxo:
 *   Frontend → POST /v1/meal-plans
 *     → API salva no PostgreSQL (status: pending_generation)
 *     → API publica na fila RabbitMQ
 *     → Worker consome fila, gera plano com IA
 *     → Worker atualiza PostgreSQL (status: completed)
 *     → Frontend consulta status via polling ou SSE
 */

import { apiClient } from './client'

export type MealPlanStatus = 'pending_generation' | 'generating' | 'completed' | 'failed'

export interface MealPlanCreate {
  client_id: string
  dietary_preferences: string[]
  goals: string[]
  restrictions?: string[]
  observations?: string
}

export interface MealPlan {
  id: string
  client_id: string
  tenant_id: string
  status: MealPlanStatus
  dietary_preferences: string[]
  goals: string[]
  restrictions: string[]
  observations: string | null
  content: string | null
  estimated_completion: string | null
  created_at: string
  updated_at: string
}

/** Cria um plano alimentar e enfileira a geração no worker */
export function createMealPlan(data: MealPlanCreate): Promise<MealPlan> {
  return apiClient.post<MealPlan>('/v1/meal-plans', data)
}

/** Busca um plano alimentar por ID */
export function getMealPlan(id: string): Promise<MealPlan> {
  return apiClient.get<MealPlan>(`/v1/meal-plans/${id}`)
}

/** Lista os planos alimentares de um cliente */
export function getClientMealPlans(clientId: string): Promise<MealPlan[]> {
  return apiClient.get<MealPlan[]>(`/v1/clients/${clientId}/meal-plans`)
}

/** Aprova um plano alimentar gerado pelo worker */
export function approveMealPlan(id: string): Promise<MealPlan> {
  return apiClient.post<MealPlan>(`/v1/meal-plans/${id}/approve`, {})
}

/** Cancela a geração de um plano */
export function cancelMealPlan(id: string): Promise<void> {
  return apiClient.delete<void>(`/v1/meal-plans/${id}`)
}
