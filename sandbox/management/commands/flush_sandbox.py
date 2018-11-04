import os
import requests
from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.contrib.auth.models import User
from datetime import datetime


def unmigrate_app(appname):
    call_command(
        'migrate',
        appname,
        'zero',
        '--noinput',
        verbosity=0
    )


def migrate_app(appname):
    call_command(
        'migrate',
        appname,
        '--noinput',
        verbosity=0
    )


def create_superuser():
    admin_username = os.environ.get('ADMIN_USERNAME', 'admin')
    admin_password = os.environ.get('ADMIN_PASSWORD', 'admin123')
    call_command(
        'createsuperuser',
        '--noinput',
        username=admin_username,
        email='admin@example.com',
        verbosity=0
    )
    admin = User.objects.get(username=admin_username)
    admin.set_password(admin_password)
    admin.save()


class Command(BaseCommand):
    """This command is called everyday morning
    and does the following:
    - Everyday: Flush all trips, passengers and alarms
    - Every week: Flush all tables
    """
    help = "Makes this a proper sandbox service by flushing some tables from time to time"

    def handle(self, *args, **options):

        # If it's not monday
        if datetime.today().weekday() != 0:
            print('Flushing trips and alarms')
            print('Un-migrating apps')
            unmigrate_app('trips')
            unmigrate_app('alarms')
            print('Un-migration complete')
            print('Migrating apps')
            migrate_app('trips')
            migrate_app('alarms')
            print('Migration complete')
            print('Flush complete')
        else:
            print('Flushing project')
            call_command(
                'flush',
                '--noinput',
                verbosity=0
            )
            print('Flush complete')
            print('Creating superuser')
            create_superuser()
            print('Superuser created')

        # Call snitch
        requests.get(os.environ.get('DEAD_MAN_SNITCH', 'http://google.com'))
