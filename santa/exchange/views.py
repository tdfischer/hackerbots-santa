from django.shortcuts import render, redirect
import datetime
from django.conf import settings
from django.contrib.auth import authenticate, login
from django.contrib import messages
from hashids import Hashids
import models
import forms

def join(request, hash):
  hasher = Hashids(settings.EXCHANGE_HASH_SALT)
  exchangeID = hasher.decrypt(hash)[0]
  exchange = models.Exchange.objects.get(id=exchangeID)

  user = request.user

  if exchange.closeDate < datetime.date.today():
    messages.error(request, "That exchange has closed.")
    return redirect('index') 

  registerForm = None
  if request.method == 'POST':
    participateForm = forms.ParticipationForm(request.POST)
    if user.is_anonymous():
      registerForm = forms.RegisterForm(request.POST)
  else:
    participateForm = forms.ParticipationForm()
    if user.is_anonymous():
      registerForm = forms.RegisterForm()

  if user.is_anonymous() and registerForm.is_valid():
    username = registerForm.cleaned_data['username']
    password = registerForm.cleaned_data['password']
    email = registerForm.cleaned_data['email']
    loginUser = authenticate(username=username, password=password)
    if not loginUser:
      if models.User.objects.filter(username=username).exists():
        messages.error(request, "That username is taken.")
      else:
        user = models.User.objects.create_user(username, email, password)
        fullName = registerForm.cleaned_data['displayName'].split(' ', 1)
        if len(fullName) == 1:
          lastName = ""
        else:
          lastName = ' '.join(fullName[1:])
        firstName = fullName[0]
        user.first_name = firstName
        user.last_name = lastName
        user.save()
        user = authenticate(username=username, password=password)
        login(request, user)
        messages.success(request, "An account was created for you.")
    else:
      messages.info(request, "You already have an account, so now you're logged in.")
      user = loginUser
      login(request, loginUser)

  if not user.is_anonymous():
    participation = models.Participant.objects.filter(user=user,
        exchange=exchange)
    if participation.exists():
        messages.info(request, "You're already signed up for that exchange, silly.")
        participation = participation[0]
    elif participateForm.is_valid():
        participation = models.Participant.objects.create(
            user = user,
            exchange = exchange,
            address = participateForm.cleaned_data['address'],
            internationalOK = participateForm.cleaned_data['internationalOK'],
            suggestions = participateForm.cleaned_data['suggestions']
        )
        messages.success(request, "The contract has been sealed. You are a part of the exchange.")
    if participation:
      return redirect('index')

  return render(request, 'santa/join.html', {'exchange': exchange,
    'registerForm': registerForm, 'participationForm': participateForm})
