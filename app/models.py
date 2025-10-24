from decimal import Decimal

from django.core.validators import RegexValidator
from django.db import models


class Payment(models.Model):
    """
    Modèle pour stocker les informations de paiement
    """

    # Validateur pour le numéro de téléphone
    phone_validator = RegexValidator(
        regex=r"^\+226\s?\d{2}\s?\d{2}\s?\d{2}\s?\d{2}$",
        message="Le numéro de téléphone doit être au format: +226 XX XX XX XX",
    )

    # Choix pour le statut du paiement
    STATUS_CHOICES = [
        ("pending", "En attente"),
        ("processing", "En cours de traitement"),
        ("completed", "Terminé"),
        ("failed", "Échoué"),
        ("cancelled", "Annulé"),
    ]

    lastname = models.CharField(max_length=100, verbose_name="Nom")
    firstname = models.CharField(max_length=100, verbose_name="Prénom")
    phone = models.CharField(max_length=20, verbose_name="Numéro de téléphone")
    amount = models.IntegerField(verbose_name="Montant (Francs CFA)")
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default="pending", verbose_name="Statut"
    )
    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name="Date de création"
    )
    updated_at = models.DateTimeField(
        auto_now=True, verbose_name="Date de modification"
    )
    reference = models.CharField(
        max_length=100, unique=True, blank=True, verbose_name="Référence de paiement"
    )
    transaction_id = models.CharField(
        max_length=100, unique=True, null=True, verbose_name="ID de transaction"
    )
    
    request_data = models.JSONField(null=True, blank=True)
    final_response = models.JSONField(null=True, blank=True)
    intermediary_response = models.JSONField(null=True, blank=True)

    class Meta:
        verbose_name = "Paiement"
        verbose_name_plural = "Paiements"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.firstname} {self.lastname} - {self.amount} Francs CFA"

    @property
    def full_name(self):
        """Retourne le nom complet"""
        return f"{self.firstname} {self.lastname}"

    @property
    def formatted_amount(self):
        """Retourne le montant formaté"""
        return f"{self.amount:,.0f} Francs CFA".replace(",", " ")
