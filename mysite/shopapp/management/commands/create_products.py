from django.core.management import BaseCommand
from shopapp.models import Product


class Command(BaseCommand):
    """
    Creating products
    """
    def handle(self, *args, **options):

        self.stdout.write('Creating products')

        product_names = [
            'Laptop',
            'Desktop',
            'Smartphone'
        ]
        for product_name in product_names:
            product_creation = Product.objects.get_or_create(name=product_name)
            if not product_creation[1]:
                self.stdout.write(f'Product "{product_name}" already exists')
            else:
                self.stdout.write(
                    self.style.SUCCESS(f'Created product {product_name}')
                )

        self.stdout.write(self.style.SUCCESS('Products creation completed'))
