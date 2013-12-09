from django.core.management.base import BaseCommand, CommandError
from santa.exchange.models import Exchange, Participant
import datetime
import random
from django.db import transaction

class ParticipantSlot(object):
  def __init__(self, data):
    self.data = data
    self.giftee = None
    self.gifter = None

  def compatible(self, other):
    if self.data == other.data:
      return False
    if not self.data.internationalOK and not (self.data.continent == other.data.continent):
      return False
    return True

  def __unicode__(self):
    return str(self.data) + " -> " + str(self.giftee.data)

  def __str__(self):
    return unicode(self)

class Matcher(object):
  def __init__(self):
    super(Matcher, self).__init__()
    self._p = []
    self._gifters = {}
    self._giftees = {}
    self._best = 0

  def add(self, participant):
    self._p.append(participant)

  @property
  def participants(self):
    return self._p

  def matched(self):
    ret = []
    for p in self._p:
      if p.gifter and p.giftee:
        ret.append(p)
    return ret

  def unmatchedGiftees(self, iter=-1):
    if iter == -1:
      iter = self._best
    ret = []
    for p in self._p:
      if p not in self._giftees[iter]:
        ret.append(p)
    return ret

  def unmatchedGifters(self, iter=-1):
    if iter == -1:
      iter = self._best
    ret = []
    for p in self._p:
      if p not in self._gifters[iter]:
        ret.append(p)
    return ret

  def unmatched(self, iter=-1):
    return set(self.unmatchedGiftees(iter)+self.unmatchedGifters(iter))

  def generateMatches(self, maxIters = 500):
    iters = 0
    self._gifters = {}
    self._giftees = {}
    iter = -1
    while iter == -1 or len(self.unmatched(iter)) > 0:
      iter += 1
      self._gifters[iter] = {}
      self._giftees[iter] = {}
      subiter = 0
      while len(self.unmatched(iter)) > 0 and subiter < maxIters:
        subiter += 1
        first = random.choice(self.unmatchedGifters(iter))
        second = random.choice(self.unmatchedGiftees(iter))
        if first.compatible(second):
          self._gifters[iter][first] = second
          self._giftees[iter][second] = first
          subiter -= 1

    self._best = 0
    for i in range(0, iter):
      unmatchCount = len(self.unmatchedGifters(i)) + len(self.unmatchedGiftees(i))
      if self._best == -1 or unmatchCount < self._best:
        self._best = i
    for gifter, giftee in self._gifters[self._best].iteritems():
      gifter.giftee = giftee
      giftee.gifter = gifter

class Command(BaseCommand):
  args = '<exchange_id exchange_id ...>'
  help = 'Matches specified exchanges'

  def handle(self, *args, **options):
    for exchange_id in args:
      try:
        exchange = Exchange.objects.get(pk=int(exchange_id))
      except Exchange.DoesNotExist:
        raise CommandError('Exchange "%s" does not exist' % exchange_id)
      match = Matcher()
      for participant in exchange.participants.all():
        match.add(ParticipantSlot(participant))
      match.generateMatches()

      print "Matches:"
      for p in match.matched():
        print "\t", p.data, '->', p.giftee.data

      print "UNMATCHED:"
      for p in match.unmatched():
        print "\t", p

      print "Patially Matched:"
      for p in match.unmatchedGiftees()+match.unmatchedGifters():
        print "\t", p.gifter, '->', p, '->', p.giftee
      if len(match.unmatchedGiftees()+match.unmatchedGifters()) > 0 or len(match.unmatched()) > 0:
          print "FAILURE"
      else:
        print "Saving exchange..."
        with transaction.atomic():
          for p in match.matched():
            print str(p.data) + "..."
            p.data.match = p.giftee.data
            p.data.save()
          exchange.matchDate = datetime.date.today()
          exchange.save()
        print "Exchange complete as of", exchange.matchDate
