
from risk_management.users.models import User

from rest_framework import serializers
from api.users.serializers import DynamicModelSerializer

from risk_register.models import (ProcessData, Processus, ClasseDeRisques, Risque, Activite, IdentificationRisque,
                                  ProcessusRisque, ActiviteRisque, Estimation, Controle, CritereDuRisque)


class ProcessDataSerialiser(serializers.ModelSerializer):
    class Meta:
        model = ProcessData
        fields = ('nom', 'origine', 'commentaire', 'clients')
        depth = 1


class UserDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'get_full_name')


class ActivityDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Activite
        fields = ('code_activite', 'nom', 'description', 'status')


class RiskDetailSerialiser(serializers.ModelSerializer):
    class Meta:
        model = ProcessusRisque
        fields = ('code_identification', 'risque', 'type_de_risque', 'created', 'verifie', 'soumis_par', 'est_assigne',
                  'proprietaire')


class RiskCriterionSerializer(serializers.ModelSerializer):
    estime_par = UserDetailSerializer(write_only=True)

    class Meta:
        model = CritereDuRisque
        fields = ('detectabilite', 'severite', 'occurence', 'estime_par')


class ProcessSerialiser(serializers.ModelSerializer):
    input_data = ProcessDataSerialiser(many=True, read_only=True)
    activites = ActivityDetailSerializer(many=True)
    proc_manager = UserDetailSerializer()
    processusrisque_set = RiskDetailSerialiser(many=True)

    class Meta:
        model = Processus
        fields = ('code_processus', 'type_processus', 'business_unit', 'nom', 'description', 'proc_manager',
                  'input_data', 'processusrisque_set', 'activites')
        extra_kwargs = {
            'type_processus': {'required': True}
        }
        # todo: activites -> hyperlinked nested field


class RiskClassSerialiser(serializers.ModelSerializer):

    class Meta:
        model = ClasseDeRisques
        fields = ('nom',)


class RiskSerialiser(DynamicModelSerializer):
    class Meta:
        model = Risque
        fields = ('code_risque', 'created', 'classe', 'modified', 'nom', 'description', 'definition',
                  'cause', 'consequence', 'couverture', 'pilotage', 'note', 'aide', 'cree_par')
        read_only_fields = ('created', 'modified')
        extra_kwargs = {
            'cree_par': {'write_only': True}
        }


class ActivitySerialiser(serializers.ModelSerializer):
    responsable = UserDetailSerializer()
    activiterisque_set = RiskDetailSerialiser(many=True)

    class Meta:
        model = Activite
        fields = ('code_activite', 'nom', 'description', 'processus', 'status', 'responsable', 'activiterisque_set',
                  'acheve_le')
        # todo: processus -> hyperlink relatedfield


class RiskIdSerialiser(serializers.ModelSerializer):
    verifie_par = UserDetailSerializer()
    class Meta:
        model = IdentificationRisque
        fields = ('code_identification', 'created', 'modified', 'risque', 'type_de_risque', 'date_revue',
                  'criterisation', 'criterisation_change', 'date_revue_change', 'verifie', 'verifie_le', 'verifie_par',
                  'seuil_de_risque', 'facteur_risque', 'status', 'est_assigne', 'get_class', 'est_obsolete')


class ProcessRiskSerialiser(RiskIdSerialiser):
    soumis_par = UserDetailSerializer()
    modifie_par = UserDetailSerializer()
    suivi_par = UserDetailSerializer(many=True)
    proprietaire = UserDetailSerializer()

    class Meta:
        model = ProcessusRisque
        fields = RiskIdSerialiser.Meta.fields + ('processus', 'soumis_par', 'modifie_par', 'suivi_par', 'proprietaire',
                                                 'proprietaire_change', )


class ActivityRiskSerialiser(RiskIdSerialiser):
    soumis_par = UserDetailSerializer()
    modifie_par = UserDetailSerializer()
    suivi_par = UserDetailSerializer(many=True)
    proprietaire = UserDetailSerializer()

    class Meta:
        model = ActiviteRisque
        fields = RiskIdSerialiser.Meta.fields + ('activite', 'soumis_par', 'modifie_par', 'suivi_par', 'proprietaire',
                                                 'proprietaire_change')


class RiskRelatedField(serializers.RelatedField):
    def to_representation(self, value):
        return value.__str__()


class EstimationSerialiser(serializers.ModelSerializer):
    content_object = RiskRelatedField(read_only=True)
    criterisation = RiskCriterionSerializer()

    class Meta:
        model = Estimation
        fields = ('code_estimation', 'created', 'modified', 'content_object', 'date_revue', 'criterisation',
                  'date_revue_change', 'criterisation_change')


class ControleSerialiser(serializers.ModelSerializer):
    content_object = RiskRelatedField(read_only=True)
    cree_par = UserDetailSerializer()
    assigne_a = UserDetailSerializer()
    modifie_par = UserDetailSerializer()

    class Meta:
        model = Controle
        fields = ('code_traitement', 'created', 'modified', 'content_object', 'start', 'end', 'critere_cible', 'nom',
                  'description', 'cree_par', 'assigne_a', 'modifie_par', 'est_approuve', 'est_valide', 'status',
                  'acheve_le', 'est_en_retard')
