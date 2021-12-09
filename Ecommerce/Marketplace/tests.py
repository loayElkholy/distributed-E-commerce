from django.test import TestCase, Client
from .models import *
from django.contrib.auth.models import User


class test(TestCase):
    def setUp(self):
        ## Create Products
        p1 = Product.objects.create(name="Ball", price=100)  ## Product with valid input
        p2 = Product.objects.create(name="Mobile", price=-100)  ## invalid price
        p3 = Product.objects.create(price=200)  ## Missing name
        ##Create Users
        u1 = User.objects.create(username="Karim", password="123456789")  ## valid input
        u2 = User.objects.create(username="Abdelrhman", password="1234567")  ## invalid password
        u3 = User.objects.create(username="Ahmed", password="12345678")  ## valid input
        u4 = User.objects.create(username="Mohamed", password="1234567")  ## invalid password
        ## Create Customer
        c1 = Customer.objects.create(user=u1, credit_card_number=5585)
        c2 = Customer.objects.create(user=u2, credit_card_number=5525)
        ##Create Seller
        s1 = Seller.objects.create(user=u3, credit_card_number=5585)
        s2 = Seller.objects.create(user=u4, credit_card_number=5575)
        ## Create Checkout
        ch1 = Checkout.objects.create(payment_method="Cash", customer=c1)
        ch2 = Checkout.objects.create(payment_method="Paypal", customer=c2)
        ## Create Order
        o1 = Order.objects.create(product=p1, quantity=2, checkout=ch1)
        o2 = Order.objects.create(product=p2, quantity=0, checkout=ch2)
        o3 = Order.objects.create(quantity=3, checkout=ch1)

    def test_customer_valid(self):
        """ Valid Customer Data """
        user = User.objects.get(username="Karim")
        c = Customer.objects.get(user=user)
        self.assertTrue(c.password_validate())

    def test_customer_invalid(self):
        """ Invalid Customer Data """

        user = User.objects.get(username="Abdelrhman")
        c = Customer.objects.get(user=user)
        self.assertFalse(c.password_validate())

    def test_seller_valid(self):
        """ Valid Seller Data """

        user = User.objects.get(username="Ahmed")
        s = Seller.objects.get(user=user)
        self.assertTrue(s.password_validate())

    def test_seller_invalid(self):
        """ Invalid Seller Data """

        user = User.objects.get(username="Mohamed")
        s = Seller.objects.get(user=user)
        self.assertFalse(s.password_validate())

    def test_product_valid(self):
        """ Valid Product Data """

        product = Product.objects.get(name="Ball")
        self.assertTrue(product.Product_Valid())

    def test_product_invalid(self):
        """ Invalid Product Price"""

        product = Product.objects.get(name="Mobile")
        self.assertFalse(product.Product_Valid())

    def test_product_noname(self):
        """ Invalid Product Name """

        product = Product.objects.get(price=200)
        self.assertFalse(product.Product_Valid())

    def test_checkout_valid(self):
        """ Valid Payment Method"""
        user = User.objects.get(username="Karim")
        customer = Customer.objects.get(user=user)
        checkout = Checkout.objects.get(customer=customer)
        self.assertTrue(checkout.Checkout_Valid())

    def test_checkout_invalid(self):
        """ Invalid Payment Method"""
        user = User.objects.get(username="Abdelrhman")
        customer = Customer.objects.get(user=user)
        checkout = Checkout.objects.get(customer=customer)
        self.assertFalse(checkout.Checkout_Valid())

    def test_order_valid(self):
        """ Valid Order"""
        order = Order.objects.get(quantity=2)
        self.assertTrue(order.Order_Valid())

    def test_order_invalid1(self):
        """ Invalid Order Quantity"""
        order = Order.objects.get(quantity=0)
        self.assertFalse(order.Order_Valid())

    def test_order_invalid2(self):
        """" Invalid Order, Doesn't Have A Product"""
        order = Order.objects.get(quantity=3)
        self.assertFalse(order.Order_Valid())

    def test_login(self):
        c = Client()
        response = c.get("/Marketplace/login")
        self.assertEqual(response.status_code, 200)

    def test_register(self):
        c = Client()
        response = c.get("/Marketplace/register")
        self.assertEqual(response.status_code, 200)

    def test_get_index(self):
        c = Client()
        response = c.get("/Marketplace/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["products"].count(), 3)

    def test_get_product(self):
        c = Client()
        response = c.get("/Marketplace/product/1")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["product"].name, "Ball")