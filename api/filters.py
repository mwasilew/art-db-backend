import django_filters

from jobs import models as jobs_models


class BuildJobFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_type='icontains')
    class Meta:
        model = jobs_models.BuildJob
        fields = ['name']

