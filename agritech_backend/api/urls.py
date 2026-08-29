from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework.routers import DefaultRouter
from django.urls import path
from .views import (
    FarmViewSet,
    SensorNodeViewSet,
    SensorReadingViewSet,
    TreatmentRecommendationViewSet,
    DiseasePredictionViewSet,
    RiskScoreViewSet,
    PredictView,
    RiskScoreView,
)

router = DefaultRouter()

router.register("farms", FarmViewSet)
router.register("sensors", SensorNodeViewSet)
router.register("readings", SensorReadingViewSet)
router.register("treatments", TreatmentRecommendationViewSet)
router.register("predictions", DiseasePredictionViewSet)
router.register("risk-scores", RiskScoreViewSet)

urlpatterns = router.urls + [
    path("predict/", PredictView.as_view()),
    path("token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path(
        "risk-score/<int:farm_id>/<str:disease>/",
        RiskScoreView.as_view()
    
    ),
]