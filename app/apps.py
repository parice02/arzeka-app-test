from django.apps import AppConfig


class AppConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "app"

    def ready(self):
        from fasoarzeka import authenticate
        from app.constant import FASOARZEKA_PASSWORD, FASOARZEKA_USERNAME

        authenticate(FASOARZEKA_USERNAME, FASOARZEKA_PASSWORD)
