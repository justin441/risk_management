
from risk_management.users.models import User

from rest_framework import serializers
from api.users.serializers import DynamicModelSerializer, UserDetailSerializer

from risk_register.models import (ProcessData, Processus, ClasseDeRisques, Risque, Activite, IdentificationRisque,
                                  ProcessusRisque, ActiviteRisque, Estimation, Controle, CritereDuRisque)


class ProcessDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProcessData
        fields = ('nom', 'origine', 'commentaire', 'clients')
        depth = 1


class RiskDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProcessusRisque
        fields = ('code_identification', 'risque', 'type_de_risque', 'created', 'verifie', 'soumis_par', 'est_assigne',
                  'proprietaire')


class RiskCriterionSerializer(serializers.ModelSerializer):
    estime_par = UserDetailSerializer(fields=('uuid', 'full_name'), write_only=True)

    class Meta:
        model = CritereDuRisque
        fields = ('detectabilite', 'severite', 'occurence', 'estime_par')


class ActivitySerializer(DynamicModelSerializer):
    responsable = UserDetailSerializer(fields=('uuid', 'full_name'))
    activiterisque_set = RiskDetailSerializer(many=True)

    class Meta:
        model = Activite
        fields = ('code_activite', 'nom', 'description', 'processus', 'status', 'responsable', 'activiterisque_set',
                  'acheve_le')


class ProcessSerializer(DynamicModelSerializer):
    input_data = ProcessDataSerializer(many=True, read_only=True)
    activites = ActivitySerializer(fields=('code_activite', 'nom', 'description', 'status'), many=True)
    proc_manager = UserDetailSerializer(fields=('uuid', 'full_name'))
    processusrisque_set = RiskDetailSerializer(many=True)

    class Meta:
        model = Processus
        fields = ('code_processus', 'type_processus', 'business_unit', 'nom', 'description', 'proc_manager',
                  'input_data', 'processusrisque_set', 'activites')
        extra_kwargs = {
            'type_processus': {'required': True}
        }


class RiskClassSerializer(serializers.ModelSerializer):

    class Meta:
        model = ClasseDeRisques
        fields = ('nom',)


class RiskSerialiser(DynamicModelSerializer):
    classe = RiskClassSerializer()
    class Meta:
        model = Risque
        fields = ('code_risque', 'created', 'classe', 'modified', 'nom', 'description', 'definition',
                  'cause', 'consequence', 'couverture', 'pilotage', 'note', 'aide', 'cree_par')
        read_only_fields = ('created', 'modified')
        extra_kwargs = {
            'cree_par': {'write_only': True},
            'classe': {'read_only': True}
        }


class RiskIdSerializer(DynamicModelSerializer):
    verifie_par = UserDetailSerializer(fields=('uuid', 'full_name'))
    risque = RiskSerialiser(fields=('code_risque', 'classe', 'nom', 'description', 'cause', 'consequence'))

    class Meta:
        model = IdentificationRisque
        fields = ('code_identification', 'created', 'modified', 'risque', 'type_de_risque', 'date_revue',
                  'criterisation', 'criterisation_change', 'date_revue_change', 'verifie', 'verifie_le', 'verifie_par',
                  'seuil_de_risque', 'facteur_risque', 'status', 'est_assigne', 'get_class', 'est_obsolete')


class ProcessRiskSerializer(RiskIdSerializer):
    soumis_par = UserDetailSerializer(fields=('uuid', 'full_name'))
    modifie_par = UserDetailSerializer(fields=('uuid', 'full_name'))
    suivi_par = UserDetailSerializer(fields=('uuid', 'full_name'), many=True)
    proprietaire = UserDetailSerializer(fields=('uuid', 'full_name'))
    processus = ProcessSerializer(fields=('code_processus', 'nom'))

    class Meta:
        model = ProcessusRisque
        fields = RiskIdSerializer.Meta.fields + ('processus', 'soumis_par', 'modifie_par', 'suivi_par', 'proprietaire',
                                                 'proprietaire_change',)


class ActivityRiskSerializer(RiskIdSerializer):
    soumis_par = UserDetailSerializer(fields=('uuid', 'full_name'))
    modifie_par = UserDetailSerializer(fields=('uuid', 'full_name'))
    suivi_par = UserDetailSerializer(fields=('uuid', 'full_name'), many=True)
    proprietaire = UserDetailSerializer(fields=('uuid', 'full_name'))
    activite = ActivitySerializer(fields=('code_activite', 'nom', 'status'))

    class Meta:
        model = ActiviteRisque
        fields = RiskIdSerializer.Meta.fields + ('activite', 'soumis_par', 'modifie_par', 'suivi_par', 'proprietaire',
                                                 'proprietaire_change')


class RiskRelatedField(serializers.RelatedField):
    def to_representation(self, value):
        if value.get_class() == 'ProcessusRisque':
            return ProcessRiskSerializer(value, fields=('code_identification', 'created', 'soumis_par', 'processus'))
        elif value.get_class() == 'ActiviteRisque':
            return ActivityRiskSerializer(value, fields=('code_identification', 'created', 'soumis_par', 'activite'))


class EstimationSerializer(serializers.ModelSerializer):
    content_object = RiskRelatedField(read_only=True)
    criterisation = RiskCriterionSerializer()

    class Meta:
        model = Estimation
        fields = ('code_estimation', 'created', 'modified', 'content_object', 'date_revue', 'criterisation',
                  'date_revue_change', 'criterisation_change')


class ControleSerializer(serializers.ModelSerializer):
    content_object = RiskRelatedField(read_only=True)
    cree_par = UserDetailSerializer(fields=('uuid', 'full_name'))
    assigne_a = UserDetailSerializer(fields=('uuid', 'full_name'))
    modifie_par = UserDetailSerializer(fields=('uuid', 'full_name'))

    class Meta:
        model = Controle
        fields = ('code_traitement', 'created', 'modified', 'content_object', 'start', 'end', 'critere_cible', 'nom',
                  'description', 'cree_par', 'assigne_a', 'modifie_par', 'est_approuve', 'est_valide', 'status',
                  'acheve_le', 'est_en_retard')
