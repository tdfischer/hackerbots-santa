from django.shortcuts import render
from django.contrib.auth.forms import AuthenticationForm

def index(request):
  if request.user.is_anonymous():
    form = AuthenticationForm()
    return render(request, 'santa/index-anonymous.html', {'login_form': form})
  else:
    return render(request, 'santa/index.html')
