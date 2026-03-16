from .base_entity import BaseEntity

class TenantEntity(BaseEntity):
    def __init__(self, id, nome, status, plano, limites, auditoria):
        self.id = id
        self.nome = nome
        self.status = status
        self.plano = plano
        self.limites = limites
        self.auditoria = auditoria