# 02. Baixar e Enviar Arquivo do Google Drive

> **Type:** n8n Flow
> **Trigger:** webhook (called by Secretária v3 or nutritionist panel)
> **Status:** active

## Short Description

Downloads a file (nutrition plan, document) from Google Drive and sends it to the client via WhatsApp/Chatwoot. Enables nutritionists to share personalized dietary plans automatically.

## Responsibilities

- Receive file ID and conversation/contact details as webhook payload
- Authenticate with Google Drive using tenant's OAuth credentials
- Download the specified file from Google Drive
- Upload file to Chatwoot as an attachment
- Send the attachment to the client via the active conversation

## Integration Points

- **Google Drive API** — file download with per-tenant OAuth
- **Chatwoot API** — file attachment upload and message sending
- **Evolution API (WhatsApp)** — file delivery channel
- **NutrIA-Pro Backend** — tenant Google credentials retrieval

## Implementation Decision

**Stay in n8n.** Low-to-medium volume, external OAuth-based API calls per tenant, triggered by events. No complex retry or bulk processing needed.
