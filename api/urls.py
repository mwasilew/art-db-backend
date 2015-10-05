from django.conf.urls import include, url
from rest_framework import routers
import views

router = routers.DefaultRouter()
router.register(r'manifest', views.ManifestViewSet)
router.register(r'result', views.ResultViewSet)
router.register(r'resultdata', views.ResultDataViewSet)
router.register(r'branch', views.BranchViewSet)
router.register(r'board', views.BoardViewSet)
router.register(r'boardconfiguration', views.BoardConfigurationViewSet)
router.register(r'benchmark', views.BenchmarkViewSet)

urlpatterns = [
    url(r'^', include(router.urls)),
    #url(r'^auth/', include('rest_framework.urls', namespace='rest_framework')),
]
