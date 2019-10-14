from datetime import datetime

import pytz
from django.conf import settings
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.core.exceptions import ValidationError
from tempus_dominus.widgets import DateTimePicker
from .models import User
from django.forms.fields import EmailField
from django import forms
from ckeditor_uploader.widgets import CKEditorUploadingWidget
from .models import Post


class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = User
        fields = ('email',)


class SignUpForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=False)
    last_name = forms.CharField(max_length=30, required=False)
    age = forms.IntegerField(required=False)

    class Meta:
        model = User
        fields = ('email', 'password1', 'password2', 'first_name', 'last_name', 'age')
        field_classes = {'email': EmailField}


def check_date(value):
    tz = pytz.timezone(settings.TIME_ZONE)
    date_now = tz.localize(datetime.now())

    if value <= date_now:
        raise ValidationError("The specified date cannot be less than or equal to the current date")


class PostForm(forms.ModelForm):
    title = forms.CharField(max_length=255)
    content = forms.CharField(required=False, widget=CKEditorUploadingWidget())
    description = forms.CharField(max_length=300, required=False)
    published = forms.BooleanField(required=False)
    attachment = forms.ImageField(required=True)
    delay = forms.BooleanField(required=False)
    delay_time = forms.DateTimeField(
        required=False,
        widget=DateTimePicker(
            attrs={
                'append': 'fa fa-calendar',
                'icon_toggle': True,
            },
            options={
                'locale': 'uk',
                'icons': {
                    'time': 'fa fa-clock',
                    'date': 'fa fa-calendar',
                    'up': 'fa fa-arrow-up',
                    'down': 'fa fa-arrow-down',
                    'previous': 'fa fa-chevron-left',
                    'next': 'fa fa-chevron-right',
                    'today': 'fa fa-calendar-check-o',
                    'clear': 'fa fa-trash',
                    'close': 'fa fa-times'
                }
            }
        ),
        input_formats=['%d.%m.%Y %H:%M:%S'],
        validators=[check_date]
    )

    class Meta:
        model = Post
        fields = ('title', 'content', 'published', 'attachment', 'delay', 'delay_time', 'description')

