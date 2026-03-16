/**
 * NutrIA-Pro — Hook: useRealtimeUpdates
 *
 * Recebe eventos em tempo real do backend via Server-Sent Events (SSE).
 *
 * O backend expõe um endpoint SSE por tenant:
 *   GET /v1/events?tenant_id={tenantId}
 *
 * Eventos suportados:
 *   - meal_plan_completed: plano alimentar gerado pelo worker está pronto
 *   - meal_plan_failed:    falha na geração do plano
 *   - new_message:         nova mensagem do cliente via Chatwoot
 *   - appointment_reminder: lembrete de consulta
 *
 * Uso:
 *   const { lastEvent, isConnected } = useRealtimeUpdates(tenantId)
 */

'use client'

import { useEffect, useRef, useState } from 'react'
import { getAccessToken } from '@/lib/api/client'

export type RealtimeEventType =
  | 'meal_plan_completed'
  | 'meal_plan_failed'
  | 'new_message'
  | 'appointment_reminder'
  | 'ping'

export interface RealtimeEvent<T = unknown> {
  type: RealtimeEventType
  data: T
  timestamp: string
}

export interface MealPlanCompletedPayload {
  meal_plan_id: string
  client_id: string
  client_name: string
}

export interface NewMessagePayload {
  conversation_id: string
  contact_name: string
  message_preview: string
}

interface UseRealtimeOptions {
  /** Intervalo de reconexão em ms após erro (padrão: 3000) */
  reconnectInterval?: number
  /** Máximo de tentativas de reconexão (padrão: 5) */
  maxReconnectAttempts?: number
  /** Callback chamado a cada evento recebido */
  onEvent?: (event: RealtimeEvent) => void
}

interface UseRealtimeReturn {
  /** Último evento recebido */
  lastEvent: RealtimeEvent | null
  /** Indica se a conexão SSE está ativa */
  isConnected: boolean
  /** Número de tentativas de reconexão realizadas */
  reconnectAttempts: number
}

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:8000'

export function useRealtimeUpdates(
  tenantId: string | null,
  options: UseRealtimeOptions = {}
): UseRealtimeReturn {
  const { reconnectInterval = 3_000, maxReconnectAttempts = 5, onEvent } = options

  const [lastEvent, setLastEvent] = useState<RealtimeEvent | null>(null)
  const [isConnected, setIsConnected] = useState(false)
  const [reconnectAttempts, setReconnectAttempts] = useState(0)

  const eventSourceRef = useRef<EventSource | null>(null)
  const reconnectTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null)
  const attemptsRef = useRef(0)

  useEffect(() => {
    if (!tenantId) return

    function connect() {
      const token = getAccessToken()
      if (!token) return

      // Fecha conexão anterior, se houver
      eventSourceRef.current?.close()

      // Nota de segurança: SSE não suporta headers personalizados no browser,
      // portanto o token é enviado como query parameter.
      // O backend deve validar este token e NÃO deve logar a URL completa.
      // Use HTTPS em produção para proteger o token em trânsito.
      const url = `${API_URL}/v1/events?tenant_id=${encodeURIComponent(tenantId!)}&token=${encodeURIComponent(token)}`
      const es = new EventSource(url)
      eventSourceRef.current = es

      es.onopen = () => {
        setIsConnected(true)
        attemptsRef.current = 0
        setReconnectAttempts(0)
      }

      es.onmessage = (event: MessageEvent<string>) => {
        try {
          const parsed = JSON.parse(event.data) as RealtimeEvent
          setLastEvent(parsed)
          onEvent?.(parsed)
        } catch {
          // ignora eventos malformados
        }
      }

      es.onerror = () => {
        setIsConnected(false)
        es.close()

        if (attemptsRef.current < maxReconnectAttempts) {
          attemptsRef.current += 1
          setReconnectAttempts(attemptsRef.current)

          reconnectTimerRef.current = setTimeout(connect, reconnectInterval)
        }
      }
    }

    connect()

    return () => {
      eventSourceRef.current?.close()
      if (reconnectTimerRef.current) {
        clearTimeout(reconnectTimerRef.current)
      }
    }
  }, [tenantId, reconnectInterval, maxReconnectAttempts, onEvent])

  return { lastEvent, isConnected, reconnectAttempts }
}
