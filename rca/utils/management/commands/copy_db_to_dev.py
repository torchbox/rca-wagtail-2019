from rca.utils.management.commands._base_copy_command import BaseCopyDatabaseCommand


class Command(BaseCopyDatabaseCommand):
    SOURCE_APP_NAME = "rca-production"
    DESTINATION_APP_NAME = "rca-development"
