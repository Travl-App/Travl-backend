from django.contrib.auth.models import AbstractUser, UnicodeUsernameValidator
from django.contrib.postgres.fields import JSONField
from django.db import models
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _


class Travler(AbstractUser):
    avatar = models.ImageField(verbose_name='Аватар', upload_to='user_avatars', blank=True, null=True)
    username_validator = UnicodeUsernameValidator()
    username = models.SlugField(_('username'),
                                unique=True, validators=[username_validator], max_length=30,
                                error_messages={
                                    'unique': _("A user with that username already exists."),
                                },)
    info = JSONField()
    is_active = models.BooleanField(default=True)
    is_author = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "User: %s" % self.username

    def serialize(self, username, detailed=True):
        if username:
            pass
        result = {
            'username': self.username,
            'modified': self.modified,
            'link': reverse_lazy('api_user:detail', kwargs={'username': self.username})
        }
        if not detailed:
            return result
        result.update({
            'is_active': self.is_active,
        })
        if self.avatar:
            result['image'] = self.avatar.url

        return result
