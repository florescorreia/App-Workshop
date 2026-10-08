"""Initial durable domain schema and append-only audit protections."""
from alembic import op
from app.db import Base
from app.models import reference_seq
revision = '0001'
down_revision = None

def upgrade():
    reference_seq.create(op.get_bind(), checkfirst=True)
    Base.metadata.create_all(op.get_bind())
    op.execute('''CREATE FUNCTION reject_audit_mutation() RETURNS trigger LANGUAGE plpgsql AS $$
      BEGIN RAISE EXCEPTION 'IdeaFlow audit events are append-only'; END; $$''')
    op.execute('CREATE TRIGGER immutable_events BEFORE UPDATE OR DELETE ON idea_event FOR EACH ROW EXECUTE FUNCTION reject_audit_mutation()')
    op.execute('''CREATE FUNCTION protect_plan_snapshot() RETURNS trigger LANGUAGE plpgsql AS $$
      BEGIN
        IF TG_TABLE_NAME = 'financial_plan_period' THEN
          IF EXISTS (SELECT 1 FROM financial_plan WHERE id = COALESCE(NEW.plan_id, OLD.plan_id) AND status <> 'Draft') THEN
            RAISE EXCEPTION 'Approved schedule is immutable';
          END IF;
        ELSIF OLD.status <> 'Draft' AND
          (NEW.annual_gross,NEW.annual_recurring,NEW.upfront,NEW.probability,NEW.confidence,NEW.rationale,NEW.approved_by,NEW.approved_at)
          IS DISTINCT FROM
          (OLD.annual_gross,OLD.annual_recurring,OLD.upfront,OLD.probability,OLD.confidence,OLD.rationale,OLD.approved_by,OLD.approved_at) THEN
          RAISE EXCEPTION 'Approved financial snapshot is immutable';
        END IF;
        RETURN COALESCE(NEW,OLD);
      END; $$''')
    op.execute('CREATE TRIGGER immutable_schedule BEFORE INSERT OR UPDATE OR DELETE ON financial_plan_period FOR EACH ROW EXECUTE FUNCTION protect_plan_snapshot()')
    op.execute('CREATE TRIGGER immutable_plan BEFORE UPDATE ON financial_plan FOR EACH ROW EXECUTE FUNCTION protect_plan_snapshot()')

def downgrade():
    raise RuntimeError('Destructive downgrade is not supported. Restore an isolated backup instead.')
