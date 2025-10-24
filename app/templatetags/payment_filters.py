import json

from django import template

register = template.Library()


@register.filter
def pprint(value):
    """Formate un dictionnaire ou JSON en JSON indenté"""
    try:
        if isinstance(value, str):
            # Si c'est une chaîne, essayer de la parser comme JSON
            parsed = json.loads(value)
        else:
            # Si c'est déjà un dictionnaire/objet
            parsed = value

        return json.dumps(parsed, indent=2, ensure_ascii=False)
    except (json.JSONDecodeError, TypeError):
        # Si ce n'est pas du JSON valide, retourner la valeur telle quelle
        return str(value)


@register.filter
def duration_since(value):
    """Calcule la durée depuis une datetime"""
    from django.utils import timezone

    if not value:
        return "N/A"

    now = timezone.now()
    duration = now - value

    if duration.days > 0:
        return f"{duration.days} jour(s)"
    elif duration.seconds > 3600:
        hours = duration.seconds // 3600
        return f"{hours} heure(s)"
    elif duration.seconds > 60:
        minutes = duration.seconds // 60
        return f"{minutes} minute(s)"
    else:
        return "Moins d'une minute"
