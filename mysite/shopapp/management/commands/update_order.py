from django.core.management import BaseCommand, CommandError

from shopapp.models import Order, Product


class Command(BaseCommand):
    """
    Updating orders
    """

    def add_arguments(self, parser):
        parser.add_argument('order_id', type=int, help='Enter an order id')

    def handle(self, *args, **options):
        order_id = options['order_id']

        try:
            order = Order.objects.get(id=order_id)
        except Order.DoesNotExist:
            raise CommandError(f'Order #{order_id} does not exists')

        products = Product.objects.all()
        for product in products:
            existing_product = order.products.filter(name=product.name).first()

            if not existing_product:
                order.products.add(product)
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Successfully added product {product.name}'
                        f' to order #{order.id}'
                    )
                )
            else:
                self.stdout.write(
                    f'Product {product.name} already exists in order #{order.id}'
                )

        order.save()

        self.stdout.write(
            self.style.SUCCESS(
                f'Adding products to order #{order.id} successfully completed'
            )
        )
