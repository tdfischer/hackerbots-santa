from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
from hashids import Hashids

class Exchange(models.Model):
  name = models.CharField(max_length=100)
  description = models.TextField()
  startDate = models.DateField()
  closeDate = models.DateField()
  matchDate = models.DateField(blank=True, null=True)
  users = models.ManyToManyField(User, related_name='exchanges', through='Participant')

  def __unicode__(self):
    return self.name

  def linkHash(self):
    hasher = Hashids(settings.EXCHANGE_HASH_SALT)
    return hasher.encrypt(self.id)

class Participant(models.Model):
  user = models.ForeignKey(User, related_name='participations')
  exchange = models.ForeignKey(Exchange)
  created = models.DateTimeField(auto_now_add=True)
  modified = models.DateTimeField(auto_now=True)
  match = models.ForeignKey('Participant', related_name='match_from', blank=True, null=True)
  address = models.TextField()
  internationalOK = models.BooleanField(default=False)
  suggestions = models.TextField()

  def __unicode__(self):
    return "%s %s"%(self.user.first_name, self.user.last_name)
