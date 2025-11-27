import django_filters
from .models import Product

class ProductFilter(django_filters.FilterSet):
    average_rating = django_filters.NumberFilter(field_name="average_rating", lookup_expr="exact")
    average_rating__gte = django_filters.NumberFilter(field_name="average_rating", lookup_expr="gte")
    average_rating__lte = django_filters.NumberFilter(field_name="average_rating", lookup_expr="lte")
    average_rating__gt = django_filters.NumberFilter(field_name="average_rating", lookup_expr="gt")
    average_rating__lt = django_filters.NumberFilter(field_name="average_rating", lookup_expr="lt")

    class Meta:
        model = Product
        fields = {
            "category": ["exact"],
            "price": ["exact", "lt", "lte", "gt", "gte"],
        }

