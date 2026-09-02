from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register('games', views.GameViewSet)
router.register('sessions', views.SessionViewSet, basename='sessions')

urlpatterns = router.urls