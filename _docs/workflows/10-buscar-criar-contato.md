# 10. Buscar ou Criar Contato + Conversa

> **Type:** n8n Flow
> **Trigger:** webhook (sub-workflow called by Secretária v3 and others)
> **Status:** active

## Short Description

A utility sub-workflow that looks up an existing Chatwoot contact by phone number, or creates a new one if not found, and ensures an active conversation exists for the contact.

## Responsibilities

- Receive phone number and tenant details as input
- Search for existing contact in Chatwoot by phone number
- Create new contact if not found (with name and phone from payload)
- Find or create an active conversation for the contact in the correct inbox
- Return contact ID and conversation ID to the calling workflow
- Sync contact data with NutrIA-Pro `clients` table

## Integration Points

- **Chatwoot API** — contact search/creation, conversation management
- **NutrIA-Pro Backend API** — client record sync
- Called by: **Secretária v3 (01)**, **05**, **09**, **11**, **13**

## Implementation Decision

**Stay in n8n.** Pure sub-workflow called by other n8n workflows. Chatwoot API calls, low volume per execution. Must remain in n8n to be callable by other n8n flows.
