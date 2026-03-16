# 00. Configurações

> **Type:** n8n Flow
> **Trigger:** referenced by all workflows (global config node)
> **Status:** active

## Short Description

Global configuration workflow providing shared environment variables, credentials, and constants used across all other n8n workflows in the NutrIA-Pro automation engine.

## Responsibilities

- Store and expose global environment variables (API keys, base URLs, tenant defaults)
- Provide shared credential references for Chatwoot, WhatsApp, Google APIs
- Define constants reused across workflows (timeout values, retry counts, message templates)

## Integration Points

- All other n8n workflows (01–13 and Retell) reference this workflow's nodes
- Environment: NutrIA-Pro backend API, Chatwoot, Evolution API (WhatsApp)

## Implementation Decision

**Stay in n8n.** This is a configuration/environment reference workflow — it has no execution logic and must remain co-located with the other workflows it supports. No migration to worker needed.
