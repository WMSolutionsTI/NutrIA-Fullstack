# ADR-008: MinIO como object storage S3-compatível

**Data:** 2026-03-09
**Status:** Aceito

---

## Contexto

O NutrIA-Pro precisa armazenar arquivos binários: planos alimentares (PDF/DOCX), backups de banco de dados, exports de workflows n8n. Precisamos de uma solução de object storage que seja self-hosted, confiável e compatível com o ecossistema S3.

## Decisão

Usar **MinIO** (self-hosted) como object storage principal.

## Alternativas Consideradas

| Alternativa | Por que descartada |
|---|---|
| AWS S3 | Vendor lock-in; custo variável; dados saem do servidor do cliente |
| Backblaze B2 | SaaS; latência adicional; sem self-hosted para dev |
| Sistema de arquivos local | Sem replicação; não escala; difícil de migrar |
| Cloudflare R2 | SaaS; sem self-hosted para dev; ainda madurando |

## Consequências

### Positivas
- **S3-compatible**: SDK boto3 funciona sem alteração com MinIO e AWS S3
- **Self-hosted**: dados de pacientes ficam no servidor do cliente (LGPD)
- **Gratuito**: sem custo de armazenamento além do disco
- **Interface web**: console nativo para gerenciar buckets
- **Path para cloud**: trocar `MINIO_ENDPOINT` por S3/B2 sem mudar código

### Negativas / Trade-offs
- Responsabilidade pela manutenção e replicação
- Consumo de disco no VPS (mitigado com retenção configurada)
- Sem CDN nativo (usar Cloudflare na frente para arquivos públicos se necessário)

## Estrutura de Buckets

```
nutria-pro-plans/          # planos alimentares por tenant
nutria-pro-backups/        # backups de banco de dados
nutria-pro-exports/        # exports de workflows n8n
```

## Referências

- https://min.io/docs/
- https://github.com/minio/minio
