from string import ascii_letters
from random import choices

from django.conf import settings
from django.contrib.auth.models import User, Permission
from django.test import TestCase
from django.urls import reverse

from .models import Product, Order
from .utils import add_two_numbers


# ***********************************************
# ************ Homework task START **************

class OrderDetailViewTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(
            username='test-user', password='test-password'
        )
        cls.user.user_permissions.add(
            Permission.objects.get(codename='view_order')
        )

    @classmethod
    def tearDownClass(cls):
        cls.user.delete()
        super().setUpClass()

    def setUp(self):
        self.client.force_login(self.user)
        self.product_1 = Product.objects.create(
            name='Test product_1', created_by=self.user
        )
        self.product_2 = Product.objects.create(
            name='Test product_2', created_by=self.user
        )
        self.order = Order.objects.create(
            delivery_address='Test address',
            promocode='test-promo',
            user=self.user
        )
        self.order.products.add(self.product_1, self.product_2)

    def tearDown(self):
        self.order.delete()
        self.product_1.delete()
        self.product_2.delete()

    def test_order_detail_view(self):
        response = self.client.get(
            reverse('shopapp:order_details',
                    kwargs={'pk': self.order.pk})
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.order.delivery_address)
        self.assertContains(response, self.order.promocode)
        self.assertEqual(response.context['object'].pk, self.order.pk)
        self.assertEqual(
            str(response.context['object'].products.all()),
            str(self.order.products.all())
        )


class OrdersDataExportViewTestCase(TestCase):
    fixtures = [
        'users-fixture.json',
        'groups-fixture.json',
        'products-fixture.json',
        'orders-fixture.json',
    ]

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(
            username='test-user', password='test-password'
        )
        cls.user.is_staff = True
        cls.user.save()

    @classmethod
    def tearDownClass(cls):
        cls.user.delete()
        super().tearDownClass()

    def setUp(self):
        self.client.force_login(self.user)

    def test_orders_data_export_view(self):
        response = self.client.get(
            reverse('shopapp:orders_export')
        )
        self.assertEqual(response.status_code, 200)
        orders = Order.objects.order_by('pk').all()
        expected_data = [
            {
                'pk': order.pk,
                'delivery_address': order.delivery_address,
                'promocode': order.promocode,
                'products': [
                    product.pk for product
                    in order.products.all()
                ],
                'user': order.user.pk
            }
            for order in orders
        ]
        orders_data = response.json()
        self.assertEqual(
            orders_data['orders'], expected_data
        )


# ************ Homework task END **************
# *********************************************


class AddTwoNumbersTestCase(TestCase):
    def test_add_two_numbers(self):
        result = add_two_numbers(2, 3)
        self.assertEqual(result, 5)


class ProductCreatViewTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='test', password='testpassword'
        )
        self.user.user_permissions.add(
            Permission.objects.get(codename='add_product')
        )
        self.product_name = ''.join(choices(ascii_letters, k=10))

    def tearDown(self):
        self.user.delete()
        Product.objects.filter(name=self.product_name).delete()

    def test_product_create(self):
        self.client.login(
            username='test', password='testpassword'
        )
        response = self.client.post(
            reverse('shopapp:product_create'),
            {
                'name': self.product_name,
                'price': '250.5',
                'description': 'Just a good to sit on',
                'discount': '10',
            }
        )
        self.assertRedirects(
            response, reverse('shopapp:products_list')
        )
        self.assertTrue(
            Product.objects.filter(name=self.product_name).exists()
        )


class ProductDetailViewTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='test')
        cls.product = Product.objects.create(
            name='Some product', created_by=cls.user
        )

    @classmethod
    def tearDownClass(cls):
        cls.user.delete()
        cls.product.delete()
        super().tearDownClass()

    def test_get_product(self):
        response = self.client.get(
            reverse('shopapp:product_details',
                    kwargs={'pk': self.product.pk})
        )
        self.assertEqual(response.status_code, 200)

    def test_get_product_and_check_content(self):
        response = self.client.get(
            reverse('shopapp:product_details',
                    kwargs={'pk': self.product.pk})
        )
        self.assertContains(response, self.product.name)


class ProductListViewTestCase(TestCase):
    fixtures = [
        'users-fixture.json',
        'groups-fixture.json',
        'products-fixture.json'
    ]

    def test_products(self):
        response = self.client.get(
            reverse('shopapp:products_list')
        )
        # for product in Product.objects.filter(archived=False).all():
        #     self.assertContains(response, product.name)
        # products = Product.objects.filter(archived=False).all()
        # products_ = response.context['object_list']
        # for p, p_ in zip(products, products_):
        #     self.assertEqual(p.pk, p_.pk)
        self.assertQuerysetEqual(
            qs=Product.objects.filter(archived=False).all(),
            values=(p.pk for p in response.context['object_list']),
            transform=lambda p: p.pk
        )
        self.assertTemplateUsed(
            response, 'shopapp/product_list.html'
        )


class OrderListViewTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # cls.credentials = dict(
        #     username='test', password='testpassword'
        # )
        # cls.user = User.objects.create_user(**cls.credentials)
        cls.user = User.objects.create_user(
            username='test', password='testpassword'
        )

    @classmethod
    def tearDownClass(cls):
        cls.user.delete()
        super().tearDownClass()

    def setUp(self):
        # self.client.login(**self.credentials)
        self.client.force_login(self.user)

    def test_orders_list_view(self):
        response = self.client.get(reverse('shopapp:orders_list'))
        self.assertContains(response, 'Orders')

    def test_orders_list_view_not_authenticated(self):
        self.client.logout()
        response = self.client.get(reverse('shopapp:orders_list'))
        self.assertEqual(response.status_code, 302)
        self.assertIn(str(settings.LOGIN_URL), response.url)


class ProductDataExportViewTestCase(TestCase):
    fixtures = [
        'users-fixture.json',
        'groups-fixture.json',
        'products-fixture.json'
    ]

    def test_product_data_export_view(self):
        response = self.client.get(
            reverse('shopapp:products_export')
        )
        self.assertEqual(response.status_code, 200)
        products = Product.objects.order_by('pk').all()
        expected_data = [
            {
                'pk': product.pk,
                'name': product.name,
                'price': str(product.price),
                'archived': product.archived
            }
            for product in products
        ]
        products_data = response.json()
        self.assertEqual(
            products_data['products'],
            expected_data
        )
