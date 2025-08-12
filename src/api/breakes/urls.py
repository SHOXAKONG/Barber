from rest_framework.routers import DefaultRouter
from .views import BreakViewSet

router = DefaultRouter()
router.register(r'break', BreakViewSet, basename='break')

urlpatterns = router.urls