from invoke import run as local
from invoke.exceptions import Exit
from invoke.tasks import task

PRODUCTION_APP_INSTANCE = "rca-production"
STAGING_APP_INSTANCE = "rca-staging"
DEV_APP_INSTANCE = "rca-development"

LOCAL_MEDIA_FOLDER = "/vagrant/media"
LOCAL_DATABASE_NAME = "rca"

USE_PRODUCTION_BACKUP = True


############
# Production
############


@task
def pull_production_media(c):
    pull_media_from_s3_heroku(c, PRODUCTION_APP_INSTANCE)


@task
def pull_production_data(c):
    if not USE_PRODUCTION_BACKUP:
        prompt_msg = (
            "This task is currently configured to pull the live "
            "production database rather than a backup. Proceeding "
            "may impact site availability. Can a backup be used "
            "instead?\n"
            'Please type the application name "{app_instance}" to '
            "proceed:\n>>> ".format(app_instance=make_bold(PRODUCTION_APP_INSTANCE))
        )
        if input(prompt_msg) != PRODUCTION_APP_INSTANCE:
            raise Exit("Aborted")

    if USE_PRODUCTION_BACKUP:
        pull_database_backup_from_heroku(c, PRODUCTION_APP_INSTANCE)
    else:
        pull_database_from_heroku(c, PRODUCTION_APP_INSTANCE)


@task
def production_shell(c):
    open_heroku_shell(c, PRODUCTION_APP_INSTANCE)


#########
# Staging
#########


@task
def pull_staging_media(c):
    pull_media_from_s3_heroku(c, STAGING_APP_INSTANCE)


@task
def pull_staging_data(c):
    pull_database_from_heroku(c, STAGING_APP_INSTANCE)


@task
def staging_shell(c):
    open_heroku_shell(c, STAGING_APP_INSTANCE)


@task
def push_staging_media(c):
    push_media_to_s3_heroku(c, STAGING_APP_INSTANCE)


#########
# Development
#########


@task
def pull_dev_media(c):
    pull_media_from_s3_heroku(c, DEV_APP_INSTANCE)


@task
def pull_dev_data(c):
    pull_database_from_heroku(c, DEV_APP_INSTANCE)


@task
def dev_shell(c):
    open_heroku_shell(c, DEV_APP_INSTANCE)


@task
def push_dev_media(c):
    push_media_to_s3_heroku(c, DEV_APP_INSTANCE)


#######
# Local
#######


def delete_local_database(c, local_database_name=LOCAL_DATABASE_NAME):
    local(
        "dropdb --if-exists {database_name}".format(database_name=LOCAL_DATABASE_NAME)
    )


########
# Heroku
########


def check_if_logged_in_to_heroku(c):
    if not local("heroku auth:whoami", warn=True):
        raise Exit(
            'Log-in with the "heroku login -i" command before running this ' "command."
        )


def get_heroku_variable(c, app_instance, variable):
    check_if_logged_in_to_heroku(c)
    return local(
        "heroku config:get {var} --app {app}".format(app=app_instance, var=variable)
    ).stdout.strip()


def pull_media_from_s3_heroku(c, app_instance):
    check_if_logged_in_to_heroku(c)
    aws_access_key_id = get_heroku_variable(c, app_instance, "AWS_ACCESS_KEY_ID")
    aws_secret_access_key = get_heroku_variable(
        c, app_instance, "AWS_SECRET_ACCESS_KEY"
    )
    aws_storage_bucket_name = get_heroku_variable(
        c, app_instance, "AWS_STORAGE_BUCKET_NAME"
    )
    pull_media_from_s3(
        c, aws_access_key_id, aws_secret_access_key, aws_storage_bucket_name
    )


def pull_database_from_heroku(c, app_instance):
    check_if_logged_in_to_heroku(c)
    delete_local_database(c)
    local(
        "heroku pg:pull --app {app} DATABASE_URL {local_database}".format(
            app=app_instance, local_database=LOCAL_DATABASE_NAME
        )
    )
    answer = (
        input(
            "Any superuser accounts you previously created locally will"
            " have been wiped. Do you wish to create a new superuser? (Y/n): "
        )
        .strip()
        .lower()
    )
    if not answer or answer == "y":
        local("django-admin createsuperuser", pty=True)


def pull_database_backup_from_heroku(c, app_instance):
    check_if_logged_in_to_heroku(c)
    local("heroku pg:backups:download --app {app}".format(app=app_instance))
    # Need to check whether previous command has succeeded
    # If an error similar to following is raised, the installed version of Postgres is
    # older than the Heroku version.
    # pg_restore: [archiver] unsupported version (1.14) in file header
    local(
        "pg_restore --clean --no-privileges --no-owner -d {local_database} latest.dump".format(
            local_database=LOCAL_DATABASE_NAME
        )
    )
    local("rm latest.dump")
    print("Database backup restored")


def open_heroku_shell(c, app_instance, shell_command="bash"):
    check_if_logged_in_to_heroku(c)
    local(
        "heroku run --app {app} {command}".format(
            app=app_instance, command=shell_command
        )
    )


####
# S3
####


def aws(c, command, aws_access_key_id, aws_secret_access_key, **kwargs):
    return local(
        "AWS_ACCESS_KEY_ID={access_key_id} AWS_SECRET_ACCESS_KEY={secret_key} "
        "aws {command}".format(
            access_key_id=aws_access_key_id,
            secret_key=aws_secret_access_key,
            command=command,
        ),
        **kwargs
    )


def pull_media_from_s3(
    c,
    aws_access_key_id,
    aws_secret_access_key,
    aws_storage_bucket_name,
    local_media_folder=LOCAL_MEDIA_FOLDER,
):
    aws_cmd = "s3 sync --delete s3://{bucket_name} {local_media}".format(
        bucket_name=aws_storage_bucket_name, local_media=local_media_folder
    )
    aws(c, aws_cmd, aws_access_key_id, aws_secret_access_key)


def push_media_to_s3(
    c,
    aws_access_key_id,
    aws_secret_access_key,
    aws_storage_bucket_name,
    local_media_folder=LOCAL_MEDIA_FOLDER,
):
    aws_cmd = "s3 sync --delete {local_media} s3://{bucket_name}/".format(
        bucket_name=aws_storage_bucket_name, local_media=local_media_folder
    )
    aws(c, aws_cmd, aws_access_key_id, aws_secret_access_key)


def push_media_to_s3_heroku(c, app_instance):
    check_if_logged_in_to_heroku(c)
    prompt_msg = (
        "You are about to push your media folder contents to the "
        "S3 bucket. It's a destructive operation. \n"
        'Please type the application name "{app_instance}" to '
        "proceed:\n>>> ".format(app_instance=make_bold(app_instance))
    )
    if input(prompt_msg) != app_instance:
        raise Exit("Aborted")
    aws_access_key_id = get_heroku_variable(c, app_instance, "AWS_ACCESS_KEY_ID")
    aws_secret_access_key = get_heroku_variable(
        c, app_instance, "AWS_SECRET_ACCESS_KEY"
    )
    aws_storage_bucket_name = get_heroku_variable(
        c, app_instance, "AWS_STORAGE_BUCKET_NAME"
    )
    push_media_to_s3(
        c, aws_access_key_id, aws_secret_access_key, aws_storage_bucket_name
    )
    aws_access_key_id = get_heroku_variable(c, app_instance, "AWS_ACCESS_KEY_ID")
    aws_secret_access_key = get_heroku_variable(
        c, app_instance, "AWS_SECRET_ACCESS_KEY"
    )
    aws_storage_bucket_name = get_heroku_variable(
        c, app_instance, "AWS_STORAGE_BUCKET_NAME"
    )
    pull_media_from_s3(
        c, aws_access_key_id, aws_secret_access_key, aws_storage_bucket_name
    )


def make_bold(msg):
    return "\033[1m{}\033[0m".format(msg)


@task
def run_tests(c):
    return local(
        "coverage erase && coverage run ./manage.py test --settings=rca.settings.test && coverage report"
    )
