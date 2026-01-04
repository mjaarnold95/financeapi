import uuid
from sqlalchemy.orm import Session
from app.models.audit_log import AuditLog

def log_audit(
    db: Session,
    *,
    entity: str,
    entity_id: uuid.UUID,
    action: str,
    before: dict | None,
    after: dict | None,
) -> None:
    db.add(AuditLog(entity=entity, entity_id=entity_id, action=action, before=before, after=after))
