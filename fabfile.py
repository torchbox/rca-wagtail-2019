from invoke import run as local
from invoke.exceptions import Exit
from invoke.tasks import task

PRODUCTION_APP_INSTANCE = "rca-production"
STAGING_APP_INSTANCE = "rca-staging"

LOCAL_MEDIA_FOLDER = "/vagrant/media"
LOCAL_DATABASE_NAME = "rca"


############
# Production
############


@task
def pull_production_media(c):
    pull_media_from_s3_heroku(c, PRODUCTION_APP_INSTANCE)


@task
def pull_production_data(c):
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
