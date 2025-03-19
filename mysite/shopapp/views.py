"""
В этом модуле находятся различные представления.

Разные view интернет-магазина: по товарам, заказам и т.д.
"""
from csv import DictWriter

import logging
from dataclasses import field
from timeit import default_timer
from datetime import datetime

from django.contrib.syndication.views import Feed
from django.contrib.auth.mixins import (LoginRequiredMixin,
                                        PermissionRequiredMixin,
                                        UserPassesTestMixin)
from django.contrib.auth.models import Group, User
from django.http import (HttpResponse, HttpRequest, HttpResponseRedirect,
                         JsonResponse)
from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import (TemplateView, ListView,
                                  DetailView, CreateView,
                                  UpdateView, DeleteView)
from rest_framework.viewsets import ModelViewSet
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, OpenApiResponse

from .models import Product, Order, ProductImage
from .forms import ProductForm, OrderForm, GroupForm
from .serializers import ProductSerializer, OrderSerializer
from .common import save_csv_products
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.core.cache import cache

log = logging.getLogger(__name__)


@extend_schema(description='Product views CRUD')
class ProductViewSet(ModelViewSet):
    """
    Набор представлений для действий над Product -
    полный CRUD для сущностей товара.
    """
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    filter_backends = [
        SearchFilter,
        OrderingFilter,
        DjangoFilterBackend,
    ]
    search_fields = ['name', 'description']
    filterset_fields = [
        'name',
        'description',
        'price',
        'discount',
        'archived',
    ]
    ordering_fields = [
        'name',
        'price',
        'discount',
    ]

    @method_decorator(cache_page(60 * 2))
    def list(self, *args, **kwargs):
        print('hello products list')
        return super().list(*args, **kwargs)

    @extend_schema(
        summary='Get one product by ID',
        description='Retrieves **product**, returns 404 if not found',
        responses={
            200: ProductSerializer,
            404: OpenApiResponse(
                description='Empty response - product not found by ID'
            )
        }
    )
    def retrieve(self, *args, **kwargs):
        return super().retrieve(*args, **kwargs)

    @action(methods=['get'], detail=False)
    def download_csv(self, request: Request):
        response = HttpResponse(content_type='text/csv')
        filename = 'products-export.csv'
        response['Content-Disposition'] = f'attachment; filename={filename}'
        queryset = self.filter_queryset(self.get_queryset())
        fields = [
            'name',
            'description',
            'price',
            'discount'
        ]
        queryset = queryset.only(*fields)
        writer = DictWriter(response, fieldnames=fields)
        writer.writeheader()

        for product in queryset:
            writer.writerow({
                field: getattr(product, field)
                for field in fields
            })

        return response

    @action(
        methods=['post'],
        detail=False,
        parser_classes=[MultiPartParser],
    )
    def upload_csv(self, request: Request):
        products = save_csv_products(
            request.FILES['file'].file,
            encoding=request.encoding,
            user=User.objects.get(pk=1),
        )
        serializer = self.get_serializer(products, many=True)
        return Response(serializer.data)


class OrderViewSet(ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    filter_backends = [
        OrderingFilter,
        DjangoFilterBackend,
    ]
    filterset_fields = [
        'delivery_address',
        'promocode',
        'user',
    ]
    ordering_fields = [
        'delivery_address',
        'created_at',
        'user',
    ]


class ShopIndexView(View):
    # @method_decorator(cache_page(60 * 2))
    def get(self, request: HttpRequest) -> HttpResponse:
        from .urls import app_name, urlpatterns

        products = [
            ('Laptop', 1999),
            ('Desktop', 2999),
            ('Smartphone', 999)
        ]

        values_to_check = ['delete', 'update', 'create', 'details', 'user_orders']

        paths = [
            (
                reverse(app_name + ':' + elem.name), elem.name.replace('_', ' ').title()
            )
            for elem in urlpatterns[2:] if not any(
                value in elem.name for value in values_to_check
            )
        ]
        context = {
            'time_running': default_timer(),
            'products': products,
            'cur_date': datetime.now(),
            'paths': paths,
            'items': 2
        }

        log.debug('Products for shop index: %s', products)
        log.info('Rendering shop index')

        print('shop index context', context)

        return render(
            request, 'shopapp/shop_index.html', context=context
        )


class GroupListView(View):
    def get(self, request: HttpRequest) -> HttpResponse:
        context = {
            'form': GroupForm(),
            'groups': Group.objects.prefetch_related('permissions').all()
        }
        return render(
            request, 'shopapp/group_list.html', context=context
        )

    def post(self, request: HttpRequest):
        form = GroupForm(request.POST)
        if form.is_valid():
            form.save()
        return redirect(request.path)


class ProductListView(ListView):
    queryset = Product.objects.filter(archived=False)


class ProductDetailView(DetailView):
    # model = Product
    queryset = Product.objects.prefetch_related('images')


class ProductCreateView(PermissionRequiredMixin, CreateView):
    permission_required = 'shopapp.add_product'
    model = Product
    fields = 'name', 'price', 'description', 'discount', 'preview'
    success_url = reverse_lazy('shopapp:products_list')

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        return super().form_valid(form)


class ProductUpdateView(UserPassesTestMixin, UpdateView):
    model = Product
    # fields = 'name', 'price', 'description', 'discount', 'preview'
    template_name_suffix = '_update_form'
    form_class = ProductForm

    def test_func(self):
        product = self.get_object()
        user = self.request.user

        return (
                user.is_superuser or
                (user.has_perm('shopapp.change_product')
                 and
                 product.created_by == user)
        )

    def get_success_url(self):
        return reverse(
            'shopapp:product_details',
            kwargs={'pk': self.object.pk}
        )

    def form_valid(self, form):
        response = super().form_valid(form)
        for image in form.files.getlist('images'):
            ProductImage.objects.create(
                product=self.object,
                image=image,
            )
        return response


class ProductDeleteView(DeleteView):
    model = Product
    success_url = reverse_lazy('shopapp:products_list')

    def form_valid(self, form):
        success_url = self.get_success_url()
        self.object.archived = True
        self.object.save()
        return HttpResponseRedirect(success_url)


class ProductDataExportView(View):
    def get(self, request: HttpRequest) -> JsonResponse:
        cache_key = 'products_data_export'
        products_data = cache.get(cache_key)
        if products_data is None:
            products = Product.objects.order_by('pk').all()
            products_data = [
                {
                    'pk': product.pk,
                    'name': product.name,
                    'price': product.price,
                    'archived': product.archived
                }
                for product in products
            ]
            cache.set(cache_key, products_data, 300)
        elem = products_data[0]
        name = elem['name']
        print('name:', name)
        return JsonResponse({'products': products_data})


class OrderListView(LoginRequiredMixin, ListView):
    queryset = (
        Order.objects
        .select_related('user')
        .prefetch_related('products')
    )


class OrderDetailView(PermissionRequiredMixin, DetailView):
    permission_required = 'shopapp.view_order'
    queryset = (
        Order.objects
        .select_related('user')
        .prefetch_related('products')
    )


class OrderCreateView(CreateView):
    template_name = 'shopapp/order_form.html'
    queryset = (
        Order.objects
        .select_related('user')
        .prefetch_related('products')
    )
    fields = 'delivery_address', 'promocode', 'user', 'products'
    success_url = reverse_lazy('shopapp:orders_list')


class OrderUpdateView(UpdateView):
    template_name = 'shopapp/order_update_form.html'
    queryset = (
        Order.objects
        .select_related('user')
        .prefetch_related('products')
    )
    fields = 'delivery_address', 'promocode', 'user', 'products'

    def get_success_url(self):
        return reverse(
            'shopapp:order_details',
            kwargs={'pk': self.object.pk}
        )


class OrderDeleteView(DeleteView):
    queryset = (
        Order.objects
        .select_related('user')
        .prefetch_related('products')
    )
    success_url = reverse_lazy('shopapp:orders_list')


class OrderDataExportView(UserPassesTestMixin, View):
    def test_func(self):
        user = self.request.user
        return user.is_staff

    def get(self, request: HttpRequest) -> JsonResponse:
        orders = Order.objects.order_by('pk').all()
        orders_data = [
            {
                'pk': order.pk,
                'delivery_address': order.delivery_address,
                'promocode': order.promocode,
                'products': [
                    product.pk for product in order.products.all()
                ],
                'user': order.user.pk
            }
            for order in orders
        ]
        return JsonResponse({'orders': orders_data})


class LatestProductsFeed(Feed):
    title = 'Latest products'
    description = 'Updates on changes and addition of products'
    link = reverse_lazy('shopapp:products_list')

    def items(self):
        return (
            (
                Product.objects
                .filter(created_at__isnull=False)
                .order_by('-created_at')[:5]
            )
        )

    def item_title(self, item: Product):
        return item.name

    def item_description(self, item: Product):
        return item.description[:200]


# ***********************************************
# ************ Homework task START **************class
class UserOrdersListView(LoginRequiredMixin, ListView):
    model = Order
    template_name = 'shopapp/user_orders_list.html'
    context_object_name = 'orders'

    def get_queryset(self):
        user_id = self.kwargs.get('user_id')
        self.owner = get_object_or_404(User, pk=user_id)
        return Order.objects.filter(user=self.owner).order_by('pk')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['owner'] = self.owner
        return context


class ExportUserOrdersView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        user_id = self.kwargs.get('user_id')
        owner = get_object_or_404(User, pk=user_id)
        cache_key = f'user_{user_id}_orders'
        orders_data = cache.get(cache_key)

        if orders_data is None:
            orders = Order.objects.filter(user=owner).order_by('pk')
            serializer = OrderSerializer(orders, many=True)
            orders_data = serializer.data
            cache.set(cache_key, orders_data, 300)

        return JsonResponse({'orders': orders_data})

# ************ Homework task END ****************
# ***********************************************
