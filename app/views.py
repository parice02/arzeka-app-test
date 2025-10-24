import json

from django.contrib import messages
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.db import models
from django.views.decorators.http import require_GET, require_POST
from django.views.generic import CreateView, DetailView, ListView, View
from fasoarzeka import check_payment, initiate_payment
from fasoarzeka.exceptions import ArzekaAPIError

from app.constant import FASOARZEKA_HASHSECRET, FASOARZEKA_MERCHANTID
from app.forms import PaymentForm
from app.models import Payment
from web.utils import convert_arzeka_payment_status, get_reference


class PaymentFormView(CreateView):
    template_name = "payment_form.html"
    form_class = PaymentForm
    model = Payment

    def get_success_url(self):
        return reverse("app:payment-detail", kwargs={"payment_id": self.payment.id})

    def form_valid(self, form):
        # Récupérer les données nettoyées
        try:
            reference = get_reference()
            form.instance.reference = reference
            self.payment: Payment = form.save()

            payment_data = {
                "amount": self.payment.amount,
                "merchant_id": FASOARZEKA_MERCHANTID,
                "hash_secret": FASOARZEKA_HASHSECRET,
                "mapped_order_id": reference,
                "additional_info": {
                    "firstname": form.cleaned_data.get("firstname"),
                    "lastname": form.cleaned_data.get("lastname"),
                    "mobile": form.cleaned_data.get("phone"),
                },
                "link_for_update_status": "http://localhost:8000"
                + reverse("app:update-payment-status"),
                "link_back_to_calling_website": "http://localhost:8000"
                + reverse("app:check-payment-status"),
            }

            response, processed_data = initiate_payment(payment_data)
            self.payment.request_data = processed_data
            self.payment.intermediary_response = response
            self.payment.save()
        except ArzekaAPIError as e:
            error_msg = "\n".join(e.response_data.values())
            messages.error(self.request, error_msg)

            return self.form_invalid(form)
        except Exception as e:
            error_msg = str(e)
            messages.error(self.request, error_msg)
            return self.form_invalid(form)

        else:
            messages.info(
                self.request,
                f"Vous serez redirigé vers la plateforme de paiement: {response.get('url','')} ",
            )

        # Ajouter un message de succès
        messages.success(self.request, "Paiement enregistré avec succès !")

        return HttpResponseRedirect(self.get_success_url())

    def form_invalid(self, form):
        """Gestion des erreurs de validation"""
        messages.error(
            self.request, "Veuillez corriger les erreurs dans le formulaire."
        )
        return self.render_to_response(self.get_context_data(form=form))


class PaymentListView(ListView):
    """Vue pour lister tous les paiements"""

    model = Payment
    template_name = "payment_list.html"
    context_object_name = "payments"
    paginate_by = 10
    ordering = ["-created_at"]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["total_payments"] = Payment.objects.count()
        context["pending_payments"] = Payment.objects.filter(status="pending").count()
        context["completed_payments"] = Payment.objects.filter(
            status="completed"
        ).count()
        return context


@require_GET
def verify_payment(request):
    """Vue AJAX pour vérifier le statut d'un paiement"""
    try:
        reference = request.GET.get("paymentRequestID")
        payment = get_object_or_404(Payment, reference=reference)

        payment = check_payment(payment.reference)

        print(payment)

        # Simuler une vérification avec l'API Fasoarzeka
        # En production, vous feriez un appel API réel
        # TODO: remplacer cette simulation par un appel réel
        return JsonResponse(
            {
                "status": "completed",
                "message": "Paiement vérifié avec succès.",
                "success": True,
            }
        )

    except ArzekaAPIError as e:
        print(e.response_data)
        return JsonResponse(
            {
                "success": False,
                "message": f"{'<br>'.join(e.response_data.values())}",
            }
        )

    except Exception as e:
        return JsonResponse({"success": False, "message": f"{str(e)}"})


class CheckPaymentStatusView(View):
    http_method_names = ["get"]
    """Vue pour vérifier le statut d'un paiement via une requête GET"""

    def get(self, request, *args, **kwargs):
        try:
            reference = request.GET.get("paymentRequestID")
            payment = Payment.objects.get(reference=reference)
            payment_data = check_payment(payment.reference)
            payment_status = convert_arzeka_payment_status(
                payment_data.get("status", "pending")
            )

            print("payment_data:", payment_data, "payment_status:", payment_status)

            # Génération de timbre

            if payment_status == "completed":
                payment.final_response = payment_data
                payment.transaction_id = payment_data.get("third_party_trans_id")
                payment.status = payment_status
                payment.save()
            else:
                intermediary_response = payment.intermediary_response

                if isinstance(intermediary_response, dict):
                    payment.intermediary_response = [
                        intermediary_response,
                        payment_data,
                    ]

                elif isinstance(intermediary_response, list):
                    intermediary_response.append(payment_data)
                    payment.intermediary_response = intermediary_response

                payment.status = payment_status
                payment.save()

            messages.info(
                request,
                f"Le statut du paiement a été mis à jour: {payment.status}",
            )

        except ArzekaAPIError as e:
            messages.info(request, f"{'<br>'.join(e.response_data.values())}")

        except Payment.DoesNotExist as e:
            messages.error(request, f"La référence {reference} n'existe pas")

        except Exception as e:
            messages.info(request, str(e))

        return HttpResponseRedirect(
            reverse("app:payment-detail", kwargs={"payment_id": payment.id})
        )


class UpdatePaymentStatusView(View):
    http_method_names = ["post"]
    """Vue pour mettre à jour le statut d'un paiement via une requête POST"""

    def post(self, request, *args, **kwargs):
        try:
            payment_data = request.POST.data
            payment = Payment.objects.get(
                reference=payment_data.get("third_party_mapped_order_id")
            )
            payment_status = convert_arzeka_payment_status(
                payment_data.get("status", "pending")
            )

            # Génération de timbre

            if payment_status == "completed":
                payment.final_response = payment_data
                payment.transaction_id = payment_data.get("third_party_trans_id")
                payment.status = payment_status
                payment.save()
            else:
                intermediary_response = payment.intermediary_response

                if isinstance(intermediary_response, dict):
                    payment.intermediary_response = [
                        intermediary_response,
                        payment_data,
                    ]

                elif isinstance(intermediary_response, list):
                    intermediary_response.append(payment_data)
                    payment.intermediary_response = intermediary_response

                payment.status = payment_status
                payment.save()

            messages.info(
                request,
                f"Le statut du paiement a été mis à jour: {payment.status}",
            )
        except Exception as e:
            pass

        return HttpResponseRedirect("/")


class PaymentDetailView(DetailView):
    """Vue pour afficher les détails d'un paiement"""

    model = Payment
    template_name = "payment_detail.html"
    context_object_name = "payment"
    pk_url_kwarg = "payment_id"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        payment = self.get_object()

        # Calculer la durée depuis la création
        import datetime

        from django.utils import timezone

        now = timezone.now()
        created = payment.created_at
        duration = now - created

        # Formatage de la durée
        if duration.days > 0:
            duration_str = f"{duration.days} jour(s)"
        elif duration.seconds > 3600:
            hours = duration.seconds // 3600
            duration_str = f"{hours} heure(s)"
        elif duration.seconds > 60:
            minutes = duration.seconds // 60
            duration_str = f"{minutes} minute(s)"
        else:
            duration_str = "Moins d'une minute"

        context["duration_since_creation"] = duration_str

        # Déterminer les actions possibles selon le statut
        context["can_verify"] = payment.status in ["pending", "processing"]
        context["can_cancel"] = payment.status in ["pending", "processing"]

        # Historique des statuts (simulé - en production, utilisez un modèle StatusHistory)
        status_history = [
            {
                "status": "pending",
                "label": "En attente",
                "timestamp": payment.created_at,
                "description": "Paiement créé et en attente de traitement",
            }
        ]

        if payment.status != "pending":
            status_history.append(
                {
                    "status": payment.status,
                    "label": payment.get_status_display(),
                    "timestamp": payment.updated_at,
                    "description": f"Statut mis à jour: {payment.get_status_display()}",
                }
            )

        context["status_history"] = status_history

        return context
