from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.utils.translation import ugettext_lazy as _
from ckeditor_uploader.fields import RichTextUploadingField
from django.db.models.signals import pre_save, pre_delete
from django.dispatch import receiver
import unidecode


class UserManager(BaseUserManager):
    """Define a model manager for User model with no username field."""

    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        """Create and save a User with the given email and password."""
        if not email:
            raise ValueError('The given email must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        """Create and save a regular User with the given email and password."""
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        """Create and save a SuperUser with the given email and password."""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(email, password, **extra_fields)


class User(AbstractUser):
    """User model."""
    username = None
    age = models.IntegerField(null=True, blank=True)
    email = models.EmailField(_('email address'), unique=True)
    sign_up_notification = models.BooleanField(
        default=False, help_text='Receive email alerts for new signups on the site')
    login_fail_notification = models.BooleanField(
        default=False, help_text='Receive email notifications about site authorization failures')
    sub_on_comments = models.BooleanField(default=True, help_text='Receive email notifications about new comments on site')
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()


class Post(models.Model):
    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, blank=True)
    content = RichTextUploadingField(blank=True, null=True)
    description = models.TextField(max_length=300, null=True, blank=True)
    published = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)
    attachment = models.ImageField()
    owner = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    delay = models.BooleanField(default=False)
    delay_time = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['published']


@receiver(pre_save, sender=Post)
def create_slug(sender, instance, **kwargs):
    instance.slug = unidecode.unidecode(instance.title).lower().replace(' ', '-')


@receiver(pre_delete, sender=Post)
def delete_task(sender, instance, **kwargs):
    instance.attachment.delete()
    from test_blog import celery
    celery.app.control.revoke(f'publication_delay_{instance.id}', terminate=True)
