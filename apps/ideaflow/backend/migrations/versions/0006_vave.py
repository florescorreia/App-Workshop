"""Add VAVE programs without modifying any existing business row."""
from alembic import op
from app.vave_models import Program, Case, ProgramEvent, Evidence, Notice, Preference
revision = '0006'
down_revision = '0005'

def upgrade():
    for model in (Program, Case, ProgramEvent, Evidence, Notice, Preference):
        model.__table__.create(op.get_bind(), checkfirst=True)
    op.execute("""DO $$ BEGIN
      IF NOT EXISTS (SELECT 1 FROM pg_trigger WHERE tgname='vave_program_event_immutable') THEN
        CREATE TRIGGER vave_program_event_immutable BEFORE UPDATE OR DELETE ON vave_program_event FOR EACH ROW EXECUTE FUNCTION reject_audit_mutation();
      END IF;
    END $$""")

def downgrade():
    raise RuntimeError('VAVE storage must be retained. Roll back code with the additive schema in place.')
