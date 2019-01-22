import unicodedata
import uuid
import logging
import random


from django.db.models.signals import pre_save
from django.dispatch import receiver

from .models import User


logger = logging.getLogger('django')


@receiver(pre_save, sender=User)
def make_username(sender, **kwargs):
    user = kwargs["instance"]
    if not user.username:
        name_list = (user.first_name + " " + user.last_name).lower().split()
        try:
            name = name_list[0] + name_list[1] + str(uuid.uuid4())
        except IndexError:
            name = name_list[0] + str(uuid.uuid4())
        username = str(unicodedata.normalize(
            'NFD', name).encode('ascii', 'ignore'), 'utf8')
        logger.info('Nouvel utilisateur ajouté: %s' % user.username)
        try:
            User.objects.get(username=username)
        except User.DoesNotExist:
            user.username = username
        else:
            make_username(sender, **kwargs)


