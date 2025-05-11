from rest_framework.test import APITestCase
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from django.urls import reverse
from base.models import Order, OrderItem, ShippingAddress, Product


class OrderListTest(APITestCase):

    def setUp(self):
        # Создаём администратора
        self.admin_user = User.objects.create_user(
            username='admin@sdu.kz',
            email='admin@sdu.kz',
            password='admin',
            is_staff=True
        )

        # Создаём обычного пользователя
        self.normal_user = User.objects.create_user(
            username='user@sdu.kz',
            email='user@sdu.kz',
            password='user'
        )

        # Продукт для заказа
        self.product = Product.objects.create(
            name='Яхина Г.: Эйзен',
            price=7450.00,
            image='images/yakhina_g_eyzen_1.webp',
            countInStock=10
        )

        # Заказ
        self.order = Order.objects.create(
            user=self.admin_user,
            paymentMethod='PayPal',
            taxPrice=610.90,
            shippingPrice=0.00,
            totalPrice=8060.90,
            isPaid=False,
            isDeliver=False
        )

        # Адрес доставки
        self.shipping = ShippingAddress.objects.create(
            order=self.order,
            address='Kurmangazy 15',
            city='Almaty',
            postalCode='050081',
            country='Kazakhstan',
        )

        # Один заказанный товар
        self.order_item = OrderItem.objects.create(
            product=self.product,
            order=self.order,
            name=self.product.name,
            qty=1,
            price=self.product.price,
            image=self.product.image
        )

        self.url = reverse('allorders')

    def get_token(self, user):
        refresh = RefreshToken.for_user(user)
        return str(refresh.access_token)

    def test_admin_can_see_orders(self):
        token = self.get_token(self.admin_user)
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['User']['email'], 'admin@sdu.kz')

    def test_user_cannot_see_orders(self):
        token = self.get_token(self.normal_user)
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_unauthenticated_cannot_access(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class OrderDetailTest(APITestCase):

    def setUp(self):
        # Админ
        self.admin_user = User.objects.create_user(
            username='admin@sdu.kz',
            email='admin@sdu.kz',
            password='admin',
            is_staff=True
        )

        # Другой пользователь
        self.other_user = User.objects.create_user(
            username='user@sdu.kz',
            email='user@sdu.kz',
            password='user'
        )

        # Продукт
        self.product = Product.objects.create(
            name='Яхина Г.: Эйзен',
            price=7450.00,
            image='images/yakhina_g_eyzen_1.webp',
            countInStock=10
        )

        # Заказ
        self.order = Order.objects.create(
            user=self.admin_user,
            paymentMethod='PayPal',
            taxPrice=610.90,
            shippingPrice=0.00,
            totalPrice=8060.90,
            isPaid=False,
            isDeliver=False
        )

        # Адрес доставки
        ShippingAddress.objects.create(
            order=self.order,
            address='Kurmangazy 15',
            city='Almaty',
            postalCode='050081',
            country='Kazakhstan',
        )

        # Товар в заказе
        OrderItem.objects.create(
            product=self.product,
            order=self.order,
            name=self.product.name,
            qty=1,
            price=self.product.price,
            image=self.product.image
        )

        self.url = reverse('user-order', kwargs={'pk': self.order._id})  # имя в urls.py

    def get_token(self, user):
        refresh = RefreshToken.for_user(user)
        return str(refresh.access_token)

    def test_admin_can_view_order(self):
        token = self.get_token(self.admin_user)
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['User']['email'], 'admin@sdu.kz')
        self.assertEqual(response.data['_id'], self.order._id)

    def test_owner_can_view_own_order(self):
        token = self.get_token(self.admin_user)
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_other_user_cannot_view_order(self):
        token = self.get_token(self.other_user)
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_unauthenticated_user_cannot_view_order(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class OrderDeliverTest(APITestCase):

    def setUp(self):
        self.admin_user = User.objects.create_user(
            username='admin@sdu.kz',
            email='admin@sdu.kz',
            password='admin',
            is_staff=True
        )

        self.normal_user = User.objects.create_user(
            username='user@sdu.kz',
            email='user@sdu.kz',
            password='user'
        )

        self.order = Order.objects.create(
            user=self.normal_user,
            paymentMethod='PayPal',
            taxPrice=610.90,
            shippingPrice=0.00,
            totalPrice=8060.90,
            isPaid=True,
            isDeliver=False
        )

        self.url = reverse('delivered', kwargs={'pk': self.order._id})

    def get_token(self, user):
        refresh = RefreshToken.for_user(user)
        return str(refresh.access_token)

    def test_admin_can_deliver_order(self):
        token = self.get_token(self.admin_user)
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)

        response = self.client.put(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, "Order was Delivered")

        self.order.refresh_from_db()
        self.assertTrue(self.order.isDeliver)
        self.assertIsNotNone(self.order.deliveredAt)

    def test_non_admin_cannot_deliver_order(self):
        token = self.get_token(self.normal_user)
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)

        response = self.client.put(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_unauthenticated_user_cannot_deliver_order(self):
        response = self.client.put(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class OrderPayTest(APITestCase):

    def setUp(self):
        self.owner = User.objects.create_user(
            username='user1@sdu.kz',
            email='user1@sdu.kz',
            password='pass'
        )

        self.other_user = User.objects.create_user(
            username='user2@sdu.kz',
            email='user2@sdu.kz',
            password='pass'
        )

        self.order = Order.objects.create(
            user=self.owner,
            paymentMethod='PayPal',
            taxPrice=610.90,
            shippingPrice=0.00,
            totalPrice=8060.90,
            isPaid=False
        )

        self.url = reverse('pay', kwargs={'pk': self.order._id})

    def get_token(self, user):
        refresh = RefreshToken.for_user(user)
        return str(refresh.access_token)

    def test_owner_can_mark_order_paid(self):
        token = self.get_token(self.owner)
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)

        response = self.client.put(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, "Order was paid")

        self.order.refresh_from_db()
        self.assertTrue(self.order.isPaid)
        self.assertIsNotNone(self.order.paidAt)

    def test_other_user_cannot_mark_order_paid(self):
        token = self.get_token(self.other_user)
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)

        response = self.client.put(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_unauthenticated_user_cannot_pay(self):
        response = self.client.put(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_order_not_found(self):
        token = self.get_token(self.owner)
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)

        response = self.client.put(reverse('pay', kwargs={'pk': 999}))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

class MyOrdersTest(APITestCase):

    def setUp(self):
        self.user1 = User.objects.create_user(
            username='user1@sdu.kz',
            email='user1@sdu.kz',
            password='pass'
        )

        self.user2 = User.objects.create_user(
            username='user2@sdu.kz',
            email='user2@sdu.kz',
            password='pass'
        )

        self.order1 = Order.objects.create(
            user=self.user1,
            paymentMethod='PayPal',
            taxPrice=610.90,
            shippingPrice=0.00,
            totalPrice=8060.90,
            isPaid=True,
            isDeliver=True
        )

        self.url = reverse('myorders')

    def get_token(self, user):
        refresh = RefreshToken.for_user(user)
        return str(refresh.access_token)

    def test_authenticated_user_receives_own_orders(self):
        token = self.get_token(self.user1)
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['_id'], self.order1._id)

    def test_user_with_no_orders_gets_empty_list(self):
        token = self.get_token(self.user2)
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, [])

    def test_unauthenticated_user_cannot_access_orders(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
