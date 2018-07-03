from django.apps import AppConfig


class RiskRegisterConfig(AppConfig):
    name = 'risk_register'

    def ready(self):
        try:
            import risk_register.signals #noqa F401
        except ImportError:
            pass
