from itertools import chain
from operator import attrgetter


def ecart_seuil_de_risque(risque):
    """
    :param risque: un objet ProcessusRisque ou ActiviteRisque
    !return: un entier compris entre -215 et 215
    la fonction prend un objet risque et renvoie la différence entre son seuil de risque et son facteur risque. si le
    risque n'est pas encore estimé, elle renvoie -215 (difference entre facteur risque min. (1^3 = 1) et
    seuil de risque max. (6^3 = 216))
    """
    if risque.seuil_de_risque() and risque.facteur_risque():
        return risque.facteur_risque() - risque.seuil_de_risque()
    else:
        return -215


def followed_risks(user):
    """
    :param user: un objet user
    :return: une liste de risques suivis par user
    """
    user_processusrisques = user.processusrisques_suivis.all()
    user_activiterisques = user.activiterisques_suivis.all()

    if user.processus_manages.all():
        for processus in user.processus_manages.all():
            user_processusrisques = user_processusrisques.union(processus.processusrisque_set.all())

    if user.activites.all():
        for activite in user.activites.all():
            user_activiterisques = user_activiterisques.union(activite.activiterisque_set.all())

    user_followed_risks = sorted(
        chain(
            user_processusrisques,
            user_activiterisques,
        ),
        key=attrgetter('created'),
        reverse=True
    )
    return user_followed_risks


def get_changes_between_2_objects(object1, object2, exclude=[]):
    changes = {}
    for field in object1._meta.fields:
        if field.value_from_object(object1) != field.value_from_object(object2):
            changes[field.name] = (field.value_from_object(object1), field.value_from_object(object2))
    return changes

