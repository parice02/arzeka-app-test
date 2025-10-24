from django.apps import AppConfig


class AppConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "app"

    def ready(self):
        from django.conf import settings
        from fasoarzeka import authenticate

        FASOARZEKA_USERNAME = getattr(settings, "FASOARZEKA_USERNAME", None)
        FASOARZEKA_PASSWORD = getattr(settings, "FASOARZEKA_PASSWORD", None)

        authenticate(FASOARZEKA_USERNAME, FASOARZEKA_PASSWORD)
