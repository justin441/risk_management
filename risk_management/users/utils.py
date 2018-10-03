from itertools import chain
from operator import attrgetter
from risk_register.models import ProcessusRisque, ActiviteRisque


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
    qs1 = user.processusrisques_manages.all()  # risques de processus assignés à l'utilisateur
    qs2 = user.activiterisques_manages.all()  # risques d'activité assignés à l'utilisateur

    # exclure les risques assignés à l'utilisateur des risques suivis par l'utilisateur
    user_processusrisques = user.processusrisques_suivis.exclude(code_identification__in=qs1)
    user_activiterisques = user.activiterisques_suivis.exclude(code_identification__in=qs2)

    if user.processus_manages.all():
        for processus in user.processus_manages.all():
            user_processusrisques = user_processusrisques.union(
                processus.processusrisque_set.exclude(code_identification__in=qs1))

    if user.activites.all():
        for activite in user.activites.all():
            user_activiterisques = user_activiterisques.union(
                activite.activiterisque_set.exclude(code_identification__in=qs2))

    user_followed_risks = sorted(
        chain(
            user_processusrisques,
            user_activiterisques,
        ),
        key=attrgetter('created'),
        reverse=True
    )
    return user_followed_risks


def get_risk_occurrences(risque):
    """
    :param risque: Objet risque
    :return: une liste de risques identifiés correspondant à l'objet risque
    """
    pr = ProcessusRisque.objects.filter(risque=risque)
    ar = ActiviteRisque.objects.filter(risque=risque)
    return sorted(
        chain(pr, ar),
        key=attrgetter('created'),
        reverse=True
    )


def get_changes_between_2_objects(object1, object2, exclude=[]):
    """"Prends 2 objets de meme modèle et retourne un dictionnaire contenant
        les attributs pour lesquels ces objets diffèrent. Utile pour savoir si un objet l'état d'un objet
        a été modifié
    """
    changes = {}
    for field in object1._meta.fields:
        if field.value_from_object(object1) != field.value_from_object(object2):
            changes[field.name] = (field.value_from_object(object1), field.value_from_object(object2))
    return changes

