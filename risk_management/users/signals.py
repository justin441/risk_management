import unicodedata
import uuid

from django.db.models.signals import pre_save
from django.dispatch import receiver

from .models import User


@receiver(pre_save, sender=User)
def make_username(sender, **kwargs):
    user = kwargs["instance"]
    if not user.username:
        name_list = (user.first_name + " " + user.last_name).lower().split()
        try:
            name = name_list[0] + name_list[1] + str(uuid.uuid4())
        except IndexError:
            name = name_list[0] + str(uuid.uuid4())
        user.username = str(unicodedata.normalize(
            'NFD', name).encode('ascii', 'ignore'), 'utf8')
