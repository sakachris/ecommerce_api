# ecommerce_api/pagination/custom.py

from django.conf import settings
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.utils.urls import replace_query_param


class ProductPagination(PageNumberPagination):
    page_size = settings.PRODUCT_PAGE_SIZE
    page_size_query_param = "page_size"
    max_page_size = 100

    def get_paginated_response(self, data):
        request = self.request
        last_page = self.page.paginator.num_pages

        return Response(
            {
                "meta": {
                    "page": self.page.number,
                    "pages": last_page,
                    "total_count": self.page.paginator.count,
                    "page_count": len(data),
                    "first_page": replace_query_param(
                        request.build_absolute_uri(), self.page_query_param, 1
                    ),
                    "last_page": replace_query_param(
                        request.build_absolute_uri(),
                        self.page_query_param,
                        last_page
                    ),
                    "next": self.get_next_link(),
                    "previous": self.get_previous_link(),
                },
                "results": data,
            }
        )


class CategoryPagination(PageNumberPagination):
    page_size = settings.CATEGORY_PAGE_SIZE
    page_size_query_param = "page_size"
    max_page_size = 100

    def get_paginated_response(self, data):
        request = self.request
        last_page = self.page.paginator.num_pages

        return Response(
            {
                "meta": {
                    "page": self.page.number,
                    "pages": last_page,
                    "total_count": self.page.paginator.count,
                    "page_count": len(data),
                    "first_page": replace_query_param(
                        request.build_absolute_uri(), self.page_query_param, 1
                    ),
                    "last_page": replace_query_param(
                        request.build_absolute_uri(),
                        self.page_query_param,
                        last_page
                    ),
                    "next": self.get_next_link(),
                    "previous": self.get_previous_link(),
                },
                "results": data,
            }
        )


class ProductImagePagination(PageNumberPagination):
    page_size = settings.PRODUCT_IMAGE_PAGE_SIZE
    page_size_query_param = "page_size"
    max_page_size = 100

    def get_paginated_response(self, data):
        request = self.request
        last_page = self.page.paginator.num_pages

        return Response(
            {
                "meta": {
                    "page": self.page.number,
                    "pages": last_page,
                    "total_count": self.page.paginator.count,
                    "page_count": len(data),
                    "first_page": replace_query_param(
                        request.build_absolute_uri(), self.page_query_param, 1
                    ),
                    "last_page": replace_query_param(
                        request.build_absolute_uri(),
                        self.page_query_param,
                        last_page
                    ),
                    "next": self.get_next_link(),
                    "previous": self.get_previous_link(),
                },
                "results": data,
            }
        )
