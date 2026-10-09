"""Explicit operator-only cleanup after a verified backup; never run at startup."""
import argparse,json,os
from sqlalchemy import create_engine,text

TABLES=['idea_event','account_event','financial_plan_period','value_period','task','comment','financial_plan','idea','demo_batch','site','category','app_session']

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--confirm-empty-workspace',required=True)
    args=parser.parse_args()
    engine=create_engine(os.environ['DATABASE_ADMIN_URL'])
    if args.confirm_empty_workspace!=engine.url.database:raise ValueError('Confirm the exact IdeaFlow database name')
    email=os.environ['ADMIN_EMAIL'].lower()
    with engine.begin() as connection:
        admin=connection.execute(text("SELECT id,password_hash FROM app_user WHERE email=:email AND role='Admin' AND active"),{'email':email}).first()
        if not admin:raise ValueError('An active bootstrap Admin is required')
        before={t:connection.scalar(text(f'SELECT count(*) FROM {t}')) for t in TABLES+['app_user']}
        # Exact table list, no CASCADE, no schema/volume/database or sequence reset.
        connection.execute(text('TRUNCATE TABLE '+','.join(TABLES)))
        connection.execute(text('DELETE FROM app_user WHERE id<>:id'),{'id':admin.id})
        assert connection.execute(text('SELECT id,password_hash FROM app_user')).first()==admin
        assert all(connection.scalar(text(f'SELECT count(*) FROM {t}'))==0 for t in TABLES)
    engine.dispose()
    print(json.dumps({'workspace':'empty','admin_login_preserved':True,'removed_counts':before,'volumes_configuration_and_reference_sequence_preserved':True},indent=2))

if __name__=='__main__':main()
