from rest_framework_nested import routers

from . import views

router = routers.DefaultRouter()
router.register('games', views.GameViewSet)
router.register('sessions', views.SessionViewSet, basename='sessions')

games_router = routers.NestedDefaultRouter(router, 'games', lookup='game')
games_router.register('sessions', views.NestedSessionViewSet, basename='game-sessions')

urlpatterns = router.urls + games_router.urls