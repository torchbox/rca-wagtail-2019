import requests
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError


class BaseCopyDatabaseCommand(BaseCommand):
    help = "Trigger a copy of a production database to another environment"

    def add_arguments(self, parser):
        parser.add_argument(
            "--media", type=bool, default=True, help="Copy the media files as well"
        )
        parser.add_argument(
            "--backup",
            type=bool,
            default=True,
            help="Create a backup of the destination database before copying",
        )
        parser.add_argument(
            "--snapshot",
            type=bool,
            default=True,
            help="Create a snapshot of the source database before copying",
        )

    def handle(self, *args, **options):
        flight_path_settings = self.get_settings()

        if flight_path_settings is None:
            raise CommandError(
                """Flightpath settings are not configured correctly. You must set
FLIGHTPATH_AUTH_KEY
FLIGHTPATH_SOURCE_KEY
FLIGHTPATH_DESTINATION_KEY
in your settings file."""
            )

        auth_key = flight_path_settings.get("FLIGHTPATH_AUTH_KEY")
        source_key = flight_path_settings.get("FLIGHTPATH_SOURCE_KEY")
        destination_key = flight_path_settings.get("FLIGHTPATH_DESTINATION_KEY")
        source_app = self.get_source_app_name
        destination_app = self.get_destination_app_name

        success, response = self.trigger_copy_database(
            auth_key,
            source_key,
            destination_key,
            source_app,
            destination_app,
            options["media"],
            options["backup"],
            options["snapshot"],
        )

        msg = self.get_job_link(response.json().get("job_id"))

        if success:
            self.stdout.write(
                self.style.SUCCESS(
                    f"Successfully started copy database to {destination_app}\n{msg}"
                )
            )
        else:
            self.stdout.write(
                self.style.ERROR(
                    f"Failed to start copy database to {destination_app}. Reason: {response.text}"
                )
            )

    @property
    def get_destination_app_name(self):
        try:
            return self.DESTINATION_APP_NAME
        except AttributeError:
            raise NotImplementedError(
                "You must define a destination_app_name attribute"
            )

    @property
    def get_source_app_name(self):
        try:
            return self.SOURCE_APP_NAME
        except AttributeError:
            raise NotImplementedError("You must define a source_app_name attribute")

    def get_settings(self):
        flight_path_settings = {
            "FLIGHTPATH_AUTH_KEY": settings.FLIGHTPATH_AUTH_KEY,
            "FLIGHTPATH_SOURCE_KEY": settings.FLIGHTPATH_SOURCE_KEY,
            "FLIGHTPATH_DESTINATION_KEY": settings.FLIGHTPATH_DESTINATION_KEY,
        }

        if all(flight_path_settings.values()):
            return flight_path_settings

    def trigger_copy_database(
        self,
        auth_key,
        source_key,
        destination_key,
        source_app,
        destination_app,
        media,
        backup,
        snapshot,
    ):

        response = requests.post(
            f"https://flightpath.torchbox.com/copy/{source_app}/{destination_app}/",
            data={
                "source_key": source_key,
                "destination_key": destination_key,
                "copy_media": media,
                "from_backup": backup,
                "create_snapshot": snapshot,
            },
            headers={
                "Authorization": f"Token {auth_key}",
            },
        )

        status = response.status_code == 200

        return status, response

    def get_job_link(self, job_id):
        return f"""To get up-to-date logs and the operation status, trigger a \n
            GET request to https://flightpath.torchbox.com/status/{job_id}/"""
