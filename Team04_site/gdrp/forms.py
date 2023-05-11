from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User, Group
from django.core.exceptions import ValidationError
from captcha.fields import ReCaptchaField
from captcha.widgets import ReCaptchaV2Checkbox
from .models import Promotion, Sponsor

class ReportsDriverPointsLogForm(forms.Form):
    SponsorID=forms.IntegerField(label="Enter Sponsor ID")

class AddProductsForm(forms.Form):
    catalog_id = forms.IntegerField()
    #Is this correct with using ebay?
    etsy_pids = forms.CharField(widget=forms.Textarea)

# genral Account creation for (unused)
class AccountCreationForm(UserCreationForm):
    first_name = forms.CharField(max_length=50, required=True, help_text="Requried")
    last_name = forms.CharField(max_length=50, required=True, help_text="Required")
    email = forms.EmailField(max_length=254, required=True, help_text="Required, please enter vaild Email")
    group = forms.ModelChoiceField(queryset=Group.objects.all(), required=True, help_text="Required")
    captcha = ReCaptchaField(widget=ReCaptchaV2Checkbox)

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'group', 'password1', 'password2')

class UserInfoUpdateForm(forms.ModelForm):
    first_name = forms.CharField(max_length=50, required=True, help_text="Requried")
    last_name = forms.CharField(max_length=50, required=True, help_text="Required")
    email = forms.EmailField(max_length=254, required=True, help_text="Required, please enter vaild Email")
    phone = forms.CharField(max_length=10)

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'phone')

    def check_phone(self):
        phone_num = self.cleaned_data.get('phone')
        if not phone_num.isdigit():
            raise forms.ValidationError("Phone number must be digits")
        return phone_num

# form for driver account creation
class DriverCreationForm(UserCreationForm):
    first_name = forms.CharField(max_length=50, required=True, help_text="Requried")
    last_name = forms.CharField(max_length=50, required=True, help_text="Required")
    email = forms.EmailField(max_length=254, required=True, help_text="Required, please enter vaild Email")
    captcha = ReCaptchaField(widget=ReCaptchaV2Checkbox)
    sponsor = forms.ModelChoiceField(queryset=Sponsor.objects.all(), empty_label=None)

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'sponsor', 'password1', 'password2')

# form for Sponsor account creation
class SponsorCreationForm(UserCreationForm):
    first_name = forms.CharField(max_length=50, required=True, help_text="Requried")
    last_name = forms.CharField(max_length=50, required=True, help_text="Required")
    email = forms.EmailField(max_length=254, required=True, help_text="Required, please enter vaild Email")
    captcha = ReCaptchaField(widget=ReCaptchaV2Checkbox)
    sponsor = forms.ModelChoiceField(queryset=Sponsor.objects.all(), empty_label=None)

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'sponsor', 'password1', 'password2')

# form for admin account creation
class AdminCreationForm(UserCreationForm):
    first_name = forms.CharField(max_length=50, required=True, help_text="Requried")
    last_name = forms.CharField(max_length=50, required=True, help_text="Required")
    email = forms.EmailField(max_length=254, required=True, help_text="Required, please enter vaild Email")
    captcha = ReCaptchaField(widget=ReCaptchaV2Checkbox)

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')

class PromoCreateForm(forms.ModelForm):
    name = forms.CharField(label="Name", max_length=255)
    description = forms.CharField(label="Description", max_length=255)
    multiplier = forms.FloatField(label="Multiplier")

    class Meta:
        model = Promotion
        fields = ('name', 'description', 'multiplier')


# extends the AuthenticationForm to add google reCaptcha
class LoginForm(AuthenticationForm):
    captcha = ReCaptchaField(widget=ReCaptchaV2Checkbox)
