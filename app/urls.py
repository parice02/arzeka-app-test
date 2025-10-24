from django.urls import path

from app import views

app_name = "app"
urlpatterns = [
    path("", views.PaymentFormView.as_view(), name="payment-form"),
    path("payments/", views.PaymentListView.as_view(), name="payment-list"),
    path(
        "payments/<int:payment_id>/",
        views.PaymentDetailView.as_view(),
        name="payment-detail",
    ),
    path("verify-payment/", views.verify_payment, name="verify-payment"),
    path(
        "check-payment-status/",
        views.CheckPaymentStatusView.as_view(),
        name="check-payment-status",
    ),
    path(
        "update-payment-status/",
        views.UpdatePaymentStatusView.as_view(),
        name="update-payment-status",
    ),
]
