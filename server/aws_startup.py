import os
import boto3
import subprocess

# steps to be run when starting this app up on AWS
def execute():
    should_run_startup_var = 'RUNNING_ON_AWS'
    if (should_run_startup_var not in os.environ) or not (os.environ[should_run_startup_var].lower() == "true"):
        return

    ssm = boto3.client('ssm', region_name='us-east-1')

    env_vars = (
        'GB_APP_KEY',
        'GB_DJANGO_SECRET_KEY',
        'GB_APP_DB_PASSWORD'
    )

    for env_var in env_vars:
        response = ssm.get_parameter(Name=env_var, WithDecryption=True)
        var_value = response['Parameter']['Value']
        os.environ[env_var] = var_value
        os.putenv(env_var, var_value)
        print(f'Set {env_var} env variable')

    should_run_migrate_var = 'RUN_MIGRATE'
    if (should_run_migrate_var not in os.environ) or (os.environ[should_run_migrate_var].lower() == "true"):
        os.environ[should_run_migrate_var] = "False"
        os.putenv(should_run_migrate_var, "False")
        print(f'Running python migrate')
        subprocess.run(["python", "manage.py", "migrate"])