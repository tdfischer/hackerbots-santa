from django.core.management.base import BaseCommand, CommandError
from django.core.mail import send_mail
from santa.exchange.models import Exchange, Participant

class Command(BaseCommand):
  args = '<exchange_id exchange_id ...>'
  help = 'Notifies matched users about exchanges'

  def handle(self, *args, **options):
    for exchange_id in args:
      try:
        exchange = Exchange.objects.get(pk=int(exchange_id))
      except Exchange.DoesNotExist:
        raise CommandError('Exchange "%s" does not exist' % exchange_id)
      if exchange.matchDate is None:
        raise CommandError('Exchange "%s" has not been matched!' % exchange_id)
      print "Sending notifications..."
      for p in exchange.participants.all():
        print str(p) + "..."
        contents = "Greetings, %s!\n\nI, the loyal robot Phong, have ran a somewhat sketchy matching algorithm on a bunch of personal data you gave me for %s. Ain't science cool?\n\nTo see the results, have a look at https://hackerbots.net/santa/." % ( p, exchange.name )
        try:
          send_mail('Seekrit Santa!', contents, 'phong@hackerbots.net',
              [p.user.email])
        except:
          print "Could not send mail to", p
