from django.conf.urls import include, url

from rest_framework import routers

from . import views

router = routers.DefaultRouter()
router.register(r'token', views.TokenViewSet)
router.register(r'manifest', views.ManifestViewSet)
router.register(r'manifest_data', views.ManifestDataViewSet)
router.register(r'manifest_reduced', views.ManifestReducedViewSet)
router.register(r'result', views.ResultViewSet)
router.register(r'resultdata', views.ResultDataViewSet)
router.register(r'benchmark', views.BenchmarkViewSet)
router.register(r'build', views.BuildViewSet)
router.register(r'branch', views.BranchViewSet)
router.register(r'testjob', views.TestJobViewSet)
router.register(r'stats', views.StatsViewSet)
router.register(r'benchmark_group_summary', views.BenchmarkGroupSummaryViewSet)

# functional view
router.register(r'compare', views.CompareResults, base_name="compare")
router.register(r'settings', views.SettingsViewSet, base_name="settings")

urlpatterns = [
    url(r'^', include(router.urls)),
    url(r'details/', views.ResultDataForManifest.as_view()),
    url(r'projects/', views.ProjectsView.as_view()),
    url(r'environments/', views.EnvironmentsView.as_view()),
    url(
        r'testjobdata/([a-zA-Z0-9_.-]+)',
        views.download_testjob_data,
        name='testjobdata'
    ),
    url(r'^dynamic_benchmark_summary/', views.dynamic_benchmark_summary),
]

