from .base_repository import BaseRepository
from app.domain.models.tenant import Tenant

class TenantRepository(BaseRepository):
    def __init__(self, db_session):
        self.db = db_session

    def get_by_inbox_id(self, inbox_id):
        return self.db.query(Tenant).filter(Tenant.chatwoot_inbox_id == inbox_id).first()

    def create(self, tenant_data):
        tenant = Tenant(**tenant_data)
        self.db.add(tenant)
        self.db.commit()
        self.db.refresh(tenant)
        return tenant