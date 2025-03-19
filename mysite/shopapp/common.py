from csv import DictReader
from io import TextIOWrapper

from shopapp.models import Product, Order


def save_csv_products(file, encoding, user):
    csv_file = TextIOWrapper(
        file,
        encoding=encoding
    )
    reader = DictReader(csv_file)

    products = [
        Product(**row, created_by=user)
        for row in reader
    ]
    Product.objects.bulk_create(products)
    return products


# ***********************************************
# ************ Homework task START **************
def save_csv_orders(file, encoding, user):
    csv_file = TextIOWrapper(
        file,
        encoding=encoding
    )
    reader = DictReader(csv_file)

    orders = []

    for row in reader:
        delivery_address = row['Delivery address']
        products = row['Products ID'].split(',')

        order = Order.objects.create(
            delivery_address=delivery_address, user=user
        )

        for product in products:
            try:
                product = Product.objects.get(
                    id=int(product.strip())
                )
                order.products.add(product)
            except Product.DoesNotExist:
                print(f'Product {product} not found.')
        orders.append(order)

    return orders
# ************ Homework task END ****************
# ***********************************************
