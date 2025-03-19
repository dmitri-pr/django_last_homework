from typing import Sequence
from django.contrib.auth.models import User
from django.core.management import BaseCommand
from django.db import transaction

from shopapp.models import Order, Product


class Command(BaseCommand):
    """
    Creating orders
    """
    @transaction.atomic
    def handle(self, *args, **options):
        self.stdout.write('Creating order with products')
        user = User.objects.get(username='admin')
        # products: Sequence[Product] = Product.objects.all()
        # products: Sequence[Product] = Product.objects.defer('description', 'price', 'created_at').all()
        products: Sequence[Product] = Product.objects.only('id', 'name').all()
        order_creation = Order.objects.get_or_create(
            delivery_address='ul. Ivanovskaya, 25-13',
            promocode='promo4',
            user=user
        )
        for product in products:
            order_creation[0].products.add(product)
        order_creation[0].save()
        if not order_creation[1]:
            self.stdout.write('Such order already exists')
        else:
            self.stdout.write(
                self.style.SUCCESS(f'Created order #{order_creation[0].id}')
            )
