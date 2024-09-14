from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import BillViewSet

router = DefaultRouter()
router.register(r"", BillViewSet, basename="bill")

urlpatterns = [
    path("", include(router.urls)),
]
