from django.core.management.base import BaseCommand, CommandError
from django.core.mail import send_mail
from santa.exchange.models import Exchange, Participant
from django.db import transaction

class Command(BaseCommand):
  args = '<exchange_id exchange_id ...>'
  help = 'Unmatches exchanges'

  def handle(self, *args, **options):
    for exchange_id in args:
      try:
        exchange = Exchange.objects.get(pk=int(exchange_id))
      except Exchange.DoesNotExist:
        raise CommandError('Exchange "%s" does not exist' % exchange_id)
      if exchange.matchDate is None:
        raise CommandError('Exchange "%s" has not been matched!' % exchange_id)
      with transaction.atomic():
        for p in exchange.participants.all():
          p.match = None
          p.save()
        exchange.matchDate = None
        exchange.save()
