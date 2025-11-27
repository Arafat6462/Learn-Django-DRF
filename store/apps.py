from django.apps import AppConfig


class StoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'store'

    # Override the ready method to import signals
    def ready(self):
        import store.signals
