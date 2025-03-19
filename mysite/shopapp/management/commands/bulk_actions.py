from django.contrib.auth.models import User
from django.core.management import BaseCommand
from shopapp.models import Product


class Command(BaseCommand):
    """
    Creating orders
    """
    def handle(self, *args, **options):
        self.stdout.write('Start demo bulk actions')

        result = Product.objects.filter(
            name__contains='Product'
        ).update(discount=10)
        print(result)

        # user = User.objects.get(username='admin')

        # info = [
        #     ('Product1', 199),
        #     ('Product2', 299),
        #     ('Product3', 399),
        # ]
        #
        # products = [
        #     Product(name=name, price=price, created_by=user)
        #     for name, price in info
        # ]
        #
        # result = Product.objects.bulk_create(products)
        #
        # for obj in result:
        #     print(obj)

        self.stdout.write('Done')
