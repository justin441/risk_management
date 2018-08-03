
def ecart_seuil_de_risque(risque):
    """
    risque -> objet ProcessusRisque ou ActiviteRisque
    return: int
    la fonction prend un objet risque et renvoie la différence entre son seuil de risque et son facteur risque. si le
    risque n'est pas encore estimé, elle renvoie -215(seuil de risque max = 6^3 = 216 et facteur risque min. = 1^3 = 1)
    """
    if risque.seuil_de_risque() and risque.facteur_risque():
        return risque.facteur_risque() - risque.seuil_de_risque()
    else:
        return -215

