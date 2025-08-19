import django_filters
from .models import NetworkNode


class NetworkNodeFilter(django_filters.FilterSet):
    """
    Фильтры для узлов сети.

    country (str): фильтр по стране.
    city (str): фильтр по городу.
    """
    country = django_filters.CharFilter(field_name="country", lookup_expr="icontains")

    class Meta:
        model = NetworkNode
        fields = ["country", "city"]
