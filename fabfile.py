import datetime
import os
import subprocess
from shlex import quote

from invoke import run as local
from invoke.exceptions import Exit
from invoke.tasks import task

# Process .env file
if os.path.exists(".env"):
    with open(".env", "r") as f:
        for line in f.readlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            var, value = line.strip().split("=", 1)
            os.environ.setdefault(var, value)

FRONTEND = os.getenv("FRONTEND", "docker")

PROJECT_DIR = "/app"

PRODUCTION_APP_INSTANCE = "rca-production"
STAGING_APP_INSTANCE = "rca-staging"
DEVELOPMENT_APP_INSTANCE = "rca-development"

LOCAL_DATABASE_NAME = PROJECT_NAME = "rca"
LOCAL_DATABASE_USERNAME = "rca"


############
# Production
############


def dexec(cmd, service="web", **kwargs):
    return local(
        "docker-compose exec -T {} bash -c {}".format(quote(service), quote(cmd)),
        **kwargs,
    )


def sudexec(cmd, service="web", **kwargs):
    return local(
        "docker-compose exec --user=root -T {} bash -c {}".format(
            quote(service), quote(cmd)
        ),
        **kwargs,
    )


@task
def build(c):
    """
    Build the development environment (call this first)
    """
    # Create mount points
    group = subprocess.check_output(["id", "-gn"], encoding="utf-8").strip()
    local("mkdir -p media database_dumps")
    local("chown -R $USER:{} media database_dumps".format(group))
    local("chmod -R 775 media database_dumps")

    if FRONTEND == "local":
        local("docker-compose up -d --build web")
    else:
        local("docker-compose up -d --build web frontend")
        dexec("npm ci", service="frontend")
    local("docker-compose stop")
    print("Project built: now run 'fab start'")


@task
def start(c):
    """
    Start the development environment
    """
    if FRONTEND == "local":
        local("docker-compose up -d web utils")
    else:
        local("docker-compose up -d web frontend utils")

    print("Use `fab sh` to enter the web container and run `djrun`")
    if FRONTEND != "local":
        print(
            "Use `fab sh --service frontend` to enter the frontend container and run `npm run start`"
        )


@task
def stop(c):
    """
    Stop the development environment
    """
    local("docker-compose stop")


@task
def restart(c):
    """
    Restart the development environment
    """
    stop(c)
    start(c)


@task
def destroy(c):
    """
    Destroy development environment containers (database will lost!)
    """
    local("docker-compose down")


@task
def sh(c, service="web"):
    """
    Run bash in a local container
    """
    subprocess.run(["docker-compose", "exec", service, "bash"])


@task
def sh_root(c, service="web"):
    """
    Run bash as root in the local web container
    """
    subprocess.run(["docker-compose", "exec", "--user=root", service, "bash"])


@task
def npm(c, command):
    print(
        f"`fab npm …` has been removed, use `fab sh --service frontend` and run `npm {command}` from there instead."
    )


@task
def psql(c, command=None):
    """
    Connect to the local postgres DB using psql
    """
    cmd_list = [
        "docker-compose",
        "exec",
        "db",
        "psql",
        *["-d", LOCAL_DATABASE_NAME],
        *["-U", LOCAL_DATABASE_USERNAME],
    ]
    if command:
        cmd_list.extend(["-c", command])

    subprocess.run(cmd_list)


def delete_docker_database(c, local_database_name=LOCAL_DATABASE_NAME):
    dexec(
        "dropdb --if-exists --host db --username={project_name} {database_name}".format(
            project_name=PROJECT_NAME, database_name=LOCAL_DATABASE_NAME
        ),
        "db",
    )
    dexec(
        "createdb --host db --username={project_name} {database_name}".format(
            project_name=PROJECT_NAME, database_name=LOCAL_DATABASE_NAME
        ),
        "db",
    )


@task
def import_data(c, database_filename):
    """
    Import local data file to the db container.
    """
    # Copy the data file to the db container
    delete_docker_database(c)
    # Import the database file to the db container
    dexec(
        "pg_restore --clean --no-acl --if-exists --no-owner --host db \
            --username={project_name} -d {database_name} {database_filename}".format(
            project_name=PROJECT_NAME,
            database_name=LOCAL_DATABASE_NAME,
            database_filename=database_filename,
        ),
        service="db",
    )
    print(
        "Any superuser accounts you previously created locally will have been wiped and will need to be recreated."
    )


def delete_local_renditions(c, local_database_name=LOCAL_DATABASE_NAME):
    try:
        psql(c, "DELETE FROM images_rendition;")
    except Exception:
        pass


#########
# Production
#########


@task
def pull_production_media(c):
    """Pull media from production AWS S3"""
    pull_media_from_s3_heroku(c, PRODUCTION_APP_INSTANCE)


@task
def pull_production_images(c):
    """Pull images from production AWS S3"""
    pull_images_from_s3_heroku(c, PRODUCTION_APP_INSTANCE)


@task
def pull_production_data(c):
    """Pull database from production Heroku Postgres"""
    pull_database_from_heroku(c, PRODUCTION_APP_INSTANCE)


# @task
# def production_shell(c):
#     """Spin up a one-time Heroku production dyno and connect to shell"""
#     open_heroku_shell(c, PRODUCTION_APP_INSTANCE)


# @task
# def push_production_media(c):
#     """Push local media content to production isntance"""
#     push_media_to_s3_heroku(c, PRODUCTION_APP_INSTANCE)


#########
# Staging
#########


@task
def pull_staging_media(c):
    """Pull media from staging AWS S3"""
    pull_media_from_s3_heroku(c, STAGING_APP_INSTANCE)


@task
def pull_staging_images(c):
    """Pull images from staging AWS S3"""
    pull_images_from_s3_heroku(c, STAGING_APP_INSTANCE)


@task
def pull_staging_data(c):
    """Pull database from staging Heroku Postgres"""
    pull_database_from_heroku(c, STAGING_APP_INSTANCE)


# @task
# def staging_shell(c):
#     """Spin up a one-time Heroku staging dyno and connect to shell"""
#     open_heroku_shell(c, STAGING_APP_INSTANCE)


# @task
# def push_staging_media(c):
#     """Push local media content to staging isntance"""
#     push_media_to_s3_heroku(c, STAGING_APP_INSTANCE)


#############
# Development
#############


@task
def pull_dev_media(c):
    """Pull media from development AWS S3"""
    pull_media_from_s3_heroku(c, DEVELOPMENT_APP_INSTANCE)


@task
def pull_dev_images(c):
    """Pull images from development AWS S3"""
    pull_images_from_s3_heroku(c, DEVELOPMENT_APP_INSTANCE)


@task
def pull_dev_data(c):
    """Pull database from development Heroku Postgres"""
    pull_database_from_heroku(c, DEVELOPMENT_APP_INSTANCE)


# @task
# def dev_shell(c):
#     """Spin up a one-time Heroku development dyno and connect to shell"""
#     open_heroku_shell(c, DEVELOPMENT_APP_INSTANCE)


# @task
# def push_dev_media(c):
#     """Push local media content to development instance"""
#     push_media_to_s3_heroku(c, DEVELOPMENT_APP_INSTANCE)


####
# S3
####


def aws(c, command, aws_access_key_id, aws_secret_access_key):
    return dexec(
        "AWS_ACCESS_KEY_ID={access_key_id} AWS_SECRET_ACCESS_KEY={secret_key} "
        "aws {command}".format(
            access_key_id=aws_access_key_id,
            secret_key=aws_secret_access_key,
            command=command,
        ),
        service="utils",
    )


def pull_media_from_s3(
    c, aws_access_key_id, aws_secret_access_key, aws_storage_bucket_name,
):
    aws_cmd = "s3 sync --delete s3://{bucket_name} /app/media".format(
        bucket_name=aws_storage_bucket_name,
    )
    aws(c, aws_cmd, aws_access_key_id, aws_secret_access_key)


def push_media_to_s3(
    c, aws_access_key_id, aws_secret_access_key, aws_storage_bucket_name,
):
    aws_cmd = "s3 sync --delete /app/media s3://{bucket_name}/".format(
        bucket_name=aws_storage_bucket_name,
    )
    aws(c, aws_cmd, aws_access_key_id, aws_secret_access_key)


def pull_images_from_s3_heroku(c, app_instance):
    check_if_logged_in_to_heroku(c)
    aws_access_key_id = get_heroku_variable(c, app_instance, "AWS_ACCESS_KEY_ID")
    aws_secret_access_key = get_heroku_variable(
        c, app_instance, "AWS_SECRET_ACCESS_KEY"
    )
    aws_storage_bucket_name = get_heroku_variable(
        c, app_instance, "AWS_STORAGE_BUCKET_NAME"
    )
    pull_images_from_s3(
        c, aws_access_key_id, aws_secret_access_key, aws_storage_bucket_name
    )


def pull_images_from_s3(
    c, aws_access_key_id, aws_secret_access_key, aws_storage_bucket_name,
):
    aws_cmd = "s3 sync --delete s3://{bucket_name}/original_images /app/media/original_images".format(
        bucket_name=aws_storage_bucket_name,
    )
    aws(c, aws_cmd, aws_access_key_id, aws_secret_access_key)
    # The above command just syncs the original images, so we need to drop the wagtailimages_renditions
    # table so that the renditions will be re-created when requested on the local build.
    delete_local_renditions(c)


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


########
# Heroku
########


@task
def heroku_login(c):
    """
    Log into the Heroku app for accessing config vars, database backups etc.
    """
    subprocess.call(["docker-compose", "exec", "utils", "heroku", "login"])


def check_if_logged_in_to_heroku(c):
    if not dexec("heroku auth:whoami", service="utils", hide="both", warn=True):
        raise Exit(
            'Log-in with the "fab heroku-login" command before running this ' "command."
        )


def check_if_heroku_app_access_granted(c, app_instance):
    check_if_logged_in_to_heroku(c)
    # Any command targeting an app would do. This one prints the list of who has access.
    result = dexec(
        f"heroku access --app {app_instance}", hide="both", warn=True, service="utils"
    )
    if result.failed:
        raise Exit(
            "You do not have access to this app. Please either try to add yourself with:\n"
            f"heroku apps:join --app {app_instance}\n\n"
            "Or ask a team admin to add you with:\n"
            f"heroku access:add <your email address> --app {app_instance}"
        )


def get_heroku_variable(c, app_instance, variable):
    check_if_logged_in_to_heroku(c)
    return dexec(
        "heroku config:get {var} --app {app}".format(app=app_instance, var=variable),
        service="utils",
        hide="both",
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
    check_if_heroku_app_access_granted(c, app_instance)

    datestamp = datetime.datetime.now().isoformat(timespec="seconds")

    dexec(
        "heroku pg:backups:download --output=/app/database_dumps/{datestamp}.dump --app {app}".format(
            app=app_instance, datestamp=datestamp,
        ),
        service="utils",
    )

    import_data(c, f"/app/database_dumps/{datestamp}.dump")

    dexec(
        "rm /app/database_dumps/{datestamp}.dump".format(datestamp=datestamp,),
        service="utils",
    )


def open_heroku_shell(c, app_instance, shell_command="bash"):
    subprocess.call(
        [
            "docker-compose",
            "exec",
            "utils",
            "heroku",
            "run",
            shell_command,
            "-a",
            app_instance,
        ]
    )


#######
# Utils
#######


def make_bold(msg):
    return "\033[1m{}\033[0m".format(msg)


@task
def dellar_snapshot(c, filename):
    """Snapshot the database, files will be stored in the db container"""
    dexec(
        "pg_dump -d {database_name} -U {database_username} > {filename}.psql".format(
            database_name=LOCAL_DATABASE_NAME,
            database_username=LOCAL_DATABASE_USERNAME,
            filename=filename,
        ),
        service="db",
    ),
    print("Database snapshot created")


@task
def dellar_restore(c, filename):
    """ Restore the database from a snapshot in the db container """
    delete_docker_database(c)

    dexec(
        "psql -U {database_username} -d {database_name} < {filename}.psql".format(
            database_name=LOCAL_DATABASE_NAME,
            database_username=LOCAL_DATABASE_USERNAME,
            filename=filename,
        ),
        service="db",
    ),
    print("Database restored.")


@task
def run_tests(c):
    return local(
        "coverage erase && coverage run ./manage.py test --settings=rca.settings.test && coverage report"
    )
