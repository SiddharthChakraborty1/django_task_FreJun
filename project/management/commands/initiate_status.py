
from django.core.management.base import BaseCommand, CommandParser, CommandError

from project.models import State




class Command(BaseCommand):
    """ Custom management command to create status in database """

    def handle(self, *args, **kwargs):
        help = ' Creates status in db that will be used by tasks '

        status = State.objects.all()
        if len(status) > 0:
            raise CommandError("Status already initiated")
        status_list = State.STATUS_List
        for status in status_list:
            State.objects.create(status=status)

        self.stdout.write(self.style.SUCCESS("Status initiated successfully!"))
