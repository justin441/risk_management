import unicodedata
import uuid
import logging


from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver

from .models import User, BusinessUnit


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
        user.username = str(unicodedata.normalize(
            'NFD', name).encode('ascii', 'ignore'), 'utf8')
        logger.info('Nouvel utilisateur ajouté: %s' % user.username)


@receiver(post_save, sender=BusinessUnit)
def send_new_bu_notice(sender, **kwargs):
    created, business_unit = kwargs['created'], kwargs['instance']
    if created:
        logger.info('New Business unit created')
        business_unit.issue_notification('created', schedule=60)
        logger.info('Notification sent.')
