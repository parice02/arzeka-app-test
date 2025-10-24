from django import forms
from django.core.validators import RegexValidator

from app.models import Payment

from fasoarzeka import initiate_payment, check_payment, authenticate
from fasoarzeka.exceptions import ArzekaAPIError

from app.constant import (
    FASOARZEKA_HASHSECRET,
    FASOARZEKA_MERCHANTID,
)


class PaymentForm(forms.ModelForm):
    """
    Formulaire de paiement basé sur le modèle Payment
    """

    class Meta:
        model = Payment
        fields = ["lastname", "firstname", "phone", "amount"]
        widgets = {
            "lastname": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Entrez votre nom",
                    "required": True,
                }
            ),
            "firstname": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Entrez votre prénom",
                    "required": True,
                }
            ),
            "phone": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "type": "tel",
                    "placeholder": "+226 XX XX XX XX",
                    "required": True,
                }
            ),
            "amount": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "min": "1",
                    "step": "1",
                    "placeholder": "Entrez le montant",
                    "required": True,
                }
            ),
        }
        error_messages = {
            "lastname": {
                "required": "Le nom est obligatoire.",
                "max_length": "Le nom ne peut pas dépasser 100 caractères.",
            },
            "firstname": {
                "required": "Le prénom est obligatoire.",
                "max_length": "Le prénom ne peut pas dépasser 100 caractères.",
            },
            "phone": {
                "required": "Le numéro de téléphone est obligatoire.",
            },
            "amount": {
                "required": "Le montant est obligatoire.",
                "min_value": "Le montant doit être supérieur à 0.",
                "invalid": "Veuillez entrer un montant valide.",
            },
        }

    def clean_lastname(self):
        """Validation personnalisée pour le nom"""
        lastname = self.cleaned_data.get("lastname")
        if lastname:
            # Supprimer les espaces en début et fin
            lastname = lastname.strip().title()
            # Vérifier qu'il ne contient que des lettres et espaces
            if not lastname.replace(" ", "").replace("-", "").isalpha():
                raise forms.ValidationError(
                    "Le nom ne doit contenir que des lettres, espaces et tirets."
                )
        return lastname

    def clean_firstname(self):
        """Validation personnalisée pour le prénom"""
        firstname = self.cleaned_data.get("firstname")
        if firstname:
            # Supprimer les espaces en début et fin
            firstname = firstname.strip().title()
            # Vérifier qu'il ne contient que des lettres et espaces
            if not firstname.replace(" ", "").replace("-", "").isalpha():
                raise forms.ValidationError(
                    "Le prénom ne doit contenir que des lettres, espaces et tirets."
                )
        return firstname

    def clean_phone(self):
        """Validation personnalisée pour le téléphone"""
        phone = self.cleaned_data.get("phone")
        if phone:
            # Supprimer tous les espaces pour la validation
            phone_clean = phone.replace(" ", "")
            # Vérifier le format
            if not phone_clean.startswith("+226") or len(phone_clean) != 12:
                raise forms.ValidationError(
                    "Le numéro doit commencer par +226 et contenir 8 chiffres."
                )
            # Reformater avec espaces
            phone = f"226{phone_clean[4:6]}{phone_clean[6:8]}{phone_clean[8:10]}{phone_clean[10:12]}"
        return phone

    def clean_amount(self):
        """Validation personnalisée pour le montant"""
        amount = self.cleaned_data.get("amount")
        if amount:
            # Vérifier que le montant est raisonnable (max 10 millions)
            if amount > 10000000:
                raise forms.ValidationError(
                    "Le montant ne peut pas dépasser 10 000 000 FCFA."
                )
            # Vérifier que le montant minimum est de 100 FCFA
            if amount < 100:
                raise forms.ValidationError("Le montant minimum est de 100 FCFA.")
        return amount

    def clean(self):
        cleaned_data = super().clean()
        # Vous pouvez ajouter des validations supplémentaires ici si nécessaire
        return cleaned_data
