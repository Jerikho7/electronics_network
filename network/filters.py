import django_filters as df
from .models import NetworkNode


class NetworkNodeFilter(df.FilterSet):
    country = df.CharFilter(field_name="country", lookup_expr="iexact")

    class Meta:
        model = NetworkNode
        fields = ["country"]
