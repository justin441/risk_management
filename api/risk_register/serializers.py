from rest_framework import serializers

from risk_register.models import (ProcessData, Processus, ClasseDeRisques, Risque, Activite, IdentificationRisque,
                                  ProcessusRisque, ActiviteRisque, Estimation, Controle)


class ProcessDataSerialiser(serializers.ModelSerializer):
    pass


class ProcessSerialiser(serializers.ModelSerializer):
    pass


class RiskClassSerialiser(serializers.ModelSerializer):
    pass


class RiskSerialiser(serializers.ModelSerializer):
    pass


class ActivitySerialiser(serializers.ModelSerializer):
    pass


class IdRiskSerialiser(serializers.ModelSerializer):
    pass


class ProcessRiskSerialiser(serializers.ModelSerializer):
    pass


class ActivityRiskSerialiser(serializers.ModelSerializer):
    pass


class EstimationSerialiser(serializers.ModelSerializer):
    pass


class ControleSerialiser(serializers.ModelSerializer):
    pass
