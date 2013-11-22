from django import forms

class ParticipationForm(forms.Form):
  address = forms.CharField(widget=forms.Textarea)
  internationalOK = forms.BooleanField(label="Are you ok with international shipping?", required=False)
  suggestions = forms.CharField(widget=forms.Textarea)

class RegisterForm(forms.Form):
  username = forms.CharField(help_text="The name you will login with")
  password = forms.CharField(widget = forms.PasswordInput)
  password_confirm = forms.CharField(widget = forms.PasswordInput)
  email = forms.EmailField()
  displayName = forms.CharField(label="Display name", help_text="The name you will be seen as")

  def clean(self):
    cleaned_data = super(RegisterForm, self).clean()
    password = cleaned_data.get('password')
    confirm = cleaned_data.get('password_confirm')
    if password != confirm:
      msg = u"Passwords do not match."
      self._errors['password'] = self.error_class([msg])
      del cleaned_data['password']
      del cleaned_data['password_confirm']
    return cleaned_data
