import pytz
from datetime import datetime
from django.core.mail import send_mail, send_mass_mail
from django.template.loader import get_template, render_to_string
from django.conf import settings
from celery import shared_task
from django.utils.html import strip_tags
from .utils import send_mass_html_mail
from .models import Post
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from .tokens import token_generator


@shared_task
def send_email(data, recipient_list, mode='login_fail'):
    email = data.get('username', 'was not provided')
    password = data.get('password', 'was not provided')
    tz = pytz.timezone(settings.TIME_ZONE)
    date = tz.localize(datetime.now())
    template = 'mail_template/login_failed.txt'
    message_info = {
        'email': email,
        'password': password,
        'date': date
    }

    if mode != 'login_fail':
        message_info.update({
            'email': data.get('email'),
            'password': data.get('password1'),
            'first_name': data.get('first_name', 'was not provided'),
            'last_name': data.get('last_name', 'was not provided'),
            'age': data.get('age', 'was not provided'),
        })
        template = 'mail_template/sign_up.txt'

    message = get_template(template).render(message_info)
    send_mail('Notification', message, settings.DEFAULT_FROM_EMAIL, recipient_list, fail_silently=True)
    return None


# task.apply_async(args, kwargs, task_id='…')
# >>> from proj.celery import app  # cancel task
# >>> app.control.revoke(task_id) # cancel task
# >>> result = my_task.AsyncResult(task_id)  #get task result
# >>> result.get()  #get task result
# task.apply_async(countdown=seconds)
@shared_task
def publication_delay(post_id):
    post = Post.objects.filter(id=post_id).first()

    if post:
        post.published = True
        post.delay = False
        post.delay_time = None
        post.save()
    return None


@shared_task
def new_comment_email_send(domain, recipient_list):
    subject = 'New comment on site'
    messages = []
    for user in recipient_list:
        data = {
            'user': user,
            'domain': domain,
            'uid': urlsafe_base64_encode(force_bytes(user.pk)),
            'token': token_generator.make_token(user),
        }
        message = render_to_string('mail_template/new_comment_added.html', data)
        plain_message = strip_tags(message)
        messages.append((subject, plain_message, message, settings.DEFAULT_FROM_EMAIL, [user.email]))

    send_mass_html_mail(messages, fail_silently=False)
    return None
