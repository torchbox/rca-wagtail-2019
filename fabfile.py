import datetime
import os
import subprocess
from shlex import quote

from invoke import run as local
from invoke.exceptions import Exit
from invoke.tasks import task

# Process .env file
if os.path.exists(".env"):
    with open(".env") as f:
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
LOCAL_DUMP_DIR = "database_dumps"
LOCAL_MEDIA_DIR = "media"
LOCAL_IMAGES_DIR = LOCAL_MEDIA_DIR + "/original_images"


############
# Production
############


def dexec(cmd, service="web", **kwargs):
    return local(
        f"docker-compose exec -T {quote(service)} bash -c {quote(cmd)}",
        **kwargs,
    )


def sudexec(cmd, service="web", **kwargs):
    return local(
        f"docker-compose exec --user=root -T {quote(service)} bash -c {quote(cmd)}",
        **kwargs,
    )


@task
def build(c):
    """
    Build the development environment (call this first)
    """
    directories_to_init = [LOCAL_DUMP_DIR, LOCAL_MEDIA_DIR]
    directories_arg = " ".join(directories_to_init)

    group = subprocess.check_output(["id", "-gn"], encoding="utf-8").strip()
    local("mkdir -p " + directories_arg)
    local(f"chown -R $USER:{group} {directories_arg}")
    local("chmod -R 775 " + directories_arg)

    local("docker-compose pull")
    local("docker-compose build")


@task
def start(c):
    """
    Start the development environment
    """
    if FRONTEND == "local":
        local("docker-compose up -d")
    else:
        local(
            "docker-compose -f docker-compose.yml -f docker/docker-compose-frontend.yml up -d"
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
        f"`fab npm …` has been removed, use `fab sh and run `npm {command}` from inside the web container instead."
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


@task
def delete_docker_database(c, local_database_name=LOCAL_DATABASE_NAME):
    dexec(
        f"dropdb --if-exists --host db --username={PROJECT_NAME} {LOCAL_DATABASE_NAME}",
        "db",
    )
    dexec(
        f"createdb --host db --username={PROJECT_NAME} {LOCAL_DATABASE_NAME}",
        "db",
    )
    # Create extension schema, for error-free restores from Heroku backups
    # (see https://devcenter.heroku.com/changelog-items/2446)
    psql(c, "CREATE SCHEMA heroku_ext;")


@task
def import_data(c, database_filename):
    """
    Import local data file to the db container.
    """
    # Copy the data file to the db container
    delete_docker_database(c)
    # Import the database file to the db container
    dexec(
        f"pg_restore --clean --no-acl --if-exists --no-owner --host db \
            --username={PROJECT_NAME} -d {LOCAL_DATABASE_NAME} {database_filename}",
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
    pull_database_from_heroku(c, PRODUCTION_APP_INSTANCE, anonymise=True)


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
    return local(
        f"AWS_ACCESS_KEY_ID={aws_access_key_id} AWS_SECRET_ACCESS_KEY={aws_secret_access_key} "
        f"aws {command}"
    )


def pull_media_from_s3(
    c,
    aws_access_key_id,
    aws_secret_access_key,
    aws_storage_bucket_name,
):
    aws_cmd = f"s3 sync --delete s3://{aws_storage_bucket_name} /app/media"
    aws(c, aws_cmd, aws_access_key_id, aws_secret_access_key)


def push_media_to_s3(
    c,
    aws_access_key_id,
    aws_secret_access_key,
    aws_storage_bucket_name,
):
    aws_cmd = f"s3 sync --delete /app/media s3://{aws_storage_bucket_name}/"
    aws(c, aws_cmd, aws_access_key_id, aws_secret_access_key)


def pull_images_from_s3_heroku(c, app_instance):
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
    c,
    aws_access_key_id,
    aws_secret_access_key,
    aws_storage_bucket_name,
):
    aws_cmd = f"s3 sync --delete s3://{aws_storage_bucket_name}/original_images /app/media/original_images"
    aws(c, aws_cmd, aws_access_key_id, aws_secret_access_key)
    # The above command just syncs the original images, so we need to drop the wagtailimages_renditions
    # table so that the renditions will be re-created when requested on the local build.
    delete_local_renditions(c)


def push_media_to_s3_heroku(c, app_instance):
    prompt_msg = (
        "You are about to push your media folder contents to the "
        "S3 bucket. It's a destructive operation. \n"
        f'Please type the application name "{make_bold(app_instance)}" to '
        "proceed:\n>>> "
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


def pull_media_from_s3_heroku(c, app_instance):
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


def pull_database_from_heroku(c, app_instance, anonymise=False):
    datestamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")

    local(
        f"heroku pg:backups:download --output={LOCAL_DUMP_DIR}/{datestamp}.dump --app {app_instance}",
    )

    import_data(c, f"/app/{LOCAL_DUMP_DIR}/{datestamp}.dump")

    local(
        f"rm {LOCAL_DUMP_DIR}/{datestamp}.dump",
    )

    if anonymise:
        dexec("./manage.py run_birdbath --skip-checks")


def open_heroku_shell(c, app_instance, shell_command="bash"):
    subprocess.call(["heroku", "run", shell_command, "-a", app_instance])


#######
# Utils
#######


def make_bold(msg):
    return f"\033[1m{msg}\033[0m"


def get_heroku_variable(c, app_instance, variable):
    return local(f"heroku config:get {variable} --app {app_instance}").stdout.strip()


@task
def dellar_snapshot(c, filename):
    """Snapshot the database, files will be stored in the db container"""
    (
        dexec(
            f"pg_dump -d {LOCAL_DATABASE_NAME} -U {LOCAL_DATABASE_USERNAME} > {filename}.psql",
            service="db",
        ),
    )
    print("Database snapshot created")


@task
def dellar_restore(c, filename):
    """Restore the database from a snapshot in the db container"""
    delete_docker_database(c)

    (
        dexec(
            f"psql -U {LOCAL_DATABASE_USERNAME} -d {LOCAL_DATABASE_NAME} < {filename}.psql",
            service="db",
        ),
    )
    print("Database restored.")


@task
def run_tests(c):
    return local(
        "coverage erase && coverage run ./manage.py test --settings=rca.settings.test && coverage report"
    )
