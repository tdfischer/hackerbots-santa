from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
from hashids import Hashids
from geocode.google import GoogleGeocoderClient
import countryinfo

class Exchange(models.Model):
  name = models.CharField(max_length=100)
  description = models.TextField()
  startDate = models.DateField()
  closeDate = models.DateField()
  matchDate = models.DateField(blank=True, null=True)
  users = models.ManyToManyField(User, related_name='exchanges', through='Participant')

  def __unicode__(self):
    return "%s (%s)" %(self.name, self.linkHash())

  def linkHash(self):
    hasher = Hashids(settings.EXCHANGE_HASH_SALT)
    return hasher.encrypt(self.id)

class Participant(models.Model):
  user = models.ForeignKey(User, related_name='participations')
  exchange = models.ForeignKey(Exchange, related_name='participants')
  created = models.DateTimeField(auto_now_add=True)
  modified = models.DateTimeField(auto_now=True)
  match = models.ForeignKey('Participant', related_name='match_from', blank=True, null=True)
  address = models.TextField()
  internationalOK = models.BooleanField(default=False)
  suggestions = models.TextField()

  @property
  def matched(self):
    return self.gifter is None

  @property
  def geocode(self):
    geo = GoogleGeocoderClient(False)
    addr = geo.geocode(self.address)
    if not addr.is_success():
      return None
    else:
      return addr[0]

  @property
  def country(self):
    geo = self.geocode
    if geo is not None:
      for c in geo['address_components']:
        if 'country' in c['types']:
          return c['short_name']
    return None

  @property
  def continent(self):
    geo = self.geocode
    if geo is not None:
      for c in geo['address_components']:
        if 'country' in c['types']:
          for country in countryinfo.countries:
            if self.country == country['code']:
              return country['continent']
    return None

  def __unicode__(self):
    return "%s %s"%(self.user.first_name, self.user.last_name)
