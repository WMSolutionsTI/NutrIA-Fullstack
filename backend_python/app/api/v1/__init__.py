from fastapi import APIRouter

from app.api.v1.admin_ops import router as admin_ops_router
from app.api.v1.agenda import router as agenda_router
from app.api.v1.admin import router as admin_router
from app.api.v1.analytics import router as analytics_router
from app.api.v1.arquivo import router as arquivo_router
from app.api.v1.auditoria import router as auditoria_router
from app.api.v1.auth import router as auth_router
from app.api.v1.caixa_de_entrada import router as caixa_de_entrada_router
from app.api.v1.campanha import router as campanha_router
from app.api.v1.chatwoot import router as chatwoot_router
from app.api.v1.cliente import router as cliente_router
from app.api.v1.contabilidade import router as contabilidade_router
from app.api.v1.conversa import router as conversa_router
from app.api.v1.estatisticas import router as estatisticas_router
from app.api.v1.exames import router as exames_router
from app.api.v1.exportacao import router as exportacao_router
from app.api.v1.integracoes_google import router as integracoes_google_router
from app.api.v1.logs import router as logs_router
from app.api.v1.monitor import router as monitor_router
from app.api.v1.n8n import router as n8n_router
from app.api.v1.nutricionista import router as nutricionista_router
from app.api.v1.onboarding import router as onboarding_router
from app.api.v1.plano import router as plano_router
from app.api.v1.plano_alimentar import router as plano_alimentar_router
from app.api.v1.prompt import router as prompt_router
from app.api.v1.prontuario import router as prontuario_router
from app.api.v1.rate_limit import router as rate_limit_router
from app.api.v1.relatorio import router as relatorio_router
from app.api.v1.suporte_nutri import router as suporte_nutri_router
from app.api.v1.tenant import router as tenant_router
from app.api.v1.voz import router as voz_router
from app.api.v1.workflow import router as workflow_router

router = APIRouter()

router.include_router(admin_router)
router.include_router(admin_ops_router)
router.include_router(agenda_router)
router.include_router(analytics_router)
router.include_router(arquivo_router)
router.include_router(auditoria_router)
router.include_router(auth_router)
router.include_router(caixa_de_entrada_router)
router.include_router(campanha_router)
router.include_router(chatwoot_router)
router.include_router(cliente_router)
router.include_router(contabilidade_router)
router.include_router(conversa_router)
router.include_router(estatisticas_router)
router.include_router(exames_router)
router.include_router(exportacao_router)
router.include_router(integracoes_google_router)
router.include_router(logs_router)
router.include_router(monitor_router)
router.include_router(n8n_router)
router.include_router(nutricionista_router)
router.include_router(onboarding_router)
router.include_router(plano_router)
router.include_router(plano_alimentar_router)
router.include_router(prompt_router)
router.include_router(prontuario_router)
router.include_router(rate_limit_router)
router.include_router(relatorio_router)
router.include_router(suporte_nutri_router)
router.include_router(tenant_router)
router.include_router(voz_router)
router.include_router(workflow_router)
