from django.utils.translation import gettext_lazy as _

from rest_framework import serializers

from risk_register.models import (ProcessData, Processus, ClasseDeRisques, Risque, Activite, IdentificationRisque,
                                  ProcessusRisque, ActiviteRisque, Estimation, Controle)


class ProcessDataSerialiser(serializers.ModelSerializer):
    class Meta:
        model = ProcessData
        fields = ('nom', 'origine', 'commentaire')


class ProcessSerialiser(serializers.ModelSerializer):
    activites = serializers.PrimaryKeyRelatedField(many=True, queryset=Activite.objects.all())

    class Meta:
        model = Processus
        fields = ('code_processus', 'type_processus', 'business_unit', 'nom', 'description', 'proc_manager',
                  'input_data', 'risques', 'activites')
        extra_kwargs = {
            'type_processus': {'required': True}
        }


class RiskClassSerialiser(serializers.ModelSerializer):
    class Meta:
        model = ClasseDeRisques
        fields = '__all__'


class RiskSerialiser(serializers.ModelSerializer):
    class Meta:
        model = Risque
        fields = ('code_risque', 'created', 'modified', 'classe', 'nom', 'description', 'definition',
                  'cause', 'consequence', 'couverture', 'pilotage', 'note', 'aide', 'cree_par')


class ActivitySerialiser(serializers.ModelSerializer):
    class Meta:
        model = Activite
        fields = '__all__'


class RiskIdSerialiser(serializers.ModelSerializer):
    class Meta:
        model = IdentificationRisque
        fields = ('code_identification', 'created', 'modified', 'risque', 'type_de_risque', 'date_revue',
                  'criterisation', 'criterisation_change', 'date_revue_change', 'verifie', 'verifie_le', 'verifie_par',
                  'seuil_de_risque', 'facteur_risque', 'status', 'est_assigne', 'get_class', 'est_obsolete')


class ProcessRiskSerialiser(RiskIdSerialiser):
    class Meta:
        model = ProcessusRisque
        fields = RiskIdSerialiser.Meta.fields + ('processus', 'soumis_par', 'modifie_par', 'suivi_par', 'proprietaire',
                                                 'proprietaire_change', 'estimations', 'controles', )


class ActivityRiskSerialiser(RiskIdSerialiser):
    class Meta:
        model = ActiviteRisque
        fields = RiskIdSerialiser.Meta.fields + ('activite', 'soumis_par', 'modifie_par', 'suivi_par', 'proprietaire',
                                                 'proprietaire_change', 'estimations', 'controles')


class EstimationSerialiser(serializers.ModelSerializer):
    class Meta:
        model = Estimation
        fields = ('code_estimation', 'created', 'modified', 'content_object', 'date_revue', 'criterisation',
                  'date_revue_change', 'criterisation_change')


class ControleSerialiser(serializers.ModelSerializer):
    class Meta:
        model = Controle
        fields = ('code_traitement', 'created', 'modified', 'content_object', 'start', 'end', 'critere_cible', 'nom',
                  'description', 'cree_par', 'assigne_a', 'modifie_par', 'est_approuve', 'est_valide', 'status',
                  'acheve_le', 'est_en_retard')
