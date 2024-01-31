import datetime

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from book.models import Book
from borrowing.models import Borrowing
from borrowing.serializers import (
    BorrowingCreateSerializer,
    BorrowingDetailSerializer,
    BorrowingSerializer,
    BorrowingListSerializer,
)

BORROWING_URL = reverse("borrowing:borrowing-list")


def detail_url(borrowing_id: int):
    return reverse("borrowing:borrowing-detail", args=[borrowing_id])


def return_url(borrowing_id: int):
    """Return URL for recipe borrowing return"""
    return reverse("borrowing:borrowing-return-borrowing", args=[borrowing_id])


def sample_book(**params):
    defaults = {
        "title": "Test Book",
        "author": "Test author",
        "cover": "hard",
        "inventory": 5,
        "daily_fee": 0.5,
    }
    defaults.update(params)

    return Book.objects.create(**defaults)


def sample_borrowing(**params):
    book = sample_book()

    defaults = {
        "borrow_date": "2024-01-31",
        "expected_return_date": "2024-02-01",
        "book": book,
    }
    defaults.update(params)

    return Borrowing.objects.create(**defaults)


def sample_user(**params):
    defaults = {
        "email": "user@user.com",
        "password": "userpass",
    }
    defaults.update(params)

    return get_user_model().objects.create_user(**defaults)


class UnauthenticatedBorrowingApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        res = self.client.get(BORROWING_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedBorrowingApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "test@test.com",
            "testpass",
        )
        self.client.force_authenticate(self.user)

    def test_list_borrowings_with_attached_current_user(self):
        another_user = sample_user()

        sample_borrowing(user_id=another_user.id)
        sample_borrowing(user_id=self.user.id)

        res = self.client.get(BORROWING_URL)

        borrowings = Borrowing.objects.filter(user=self.user.id)
        serializer = BorrowingListSerializer(borrowings, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_filter_borrowings_by_is_active(self):
        borrowing = sample_borrowing(user_id=self.user.id)
        borrowing_with_return_date = sample_borrowing(
            user_id=self.user.id, actual_return_date="2024-02-01"
        )

        res = self.client.get(BORROWING_URL, {"is_active": True})

        serializer1 = BorrowingListSerializer(borrowing)
        serializer2 = BorrowingListSerializer(borrowing_with_return_date)

        self.assertIn(serializer1.data, res.data)
        self.assertNotIn(serializer2.data, res.data)

    def test_filter_borrowings_by_user_id_not_works_for_default_user(self):
        another_user = sample_user()
        borrowing = sample_borrowing(user_id=self.user.id)
        borrowing_with_another_user = sample_borrowing(
            user_id=another_user.id
        )

        res = self.client.get(BORROWING_URL, {"user_id": another_user.id})

        serializer1 = BorrowingListSerializer(borrowing)
        serializer2 = BorrowingListSerializer(borrowing_with_another_user)

        self.assertIn(serializer1.data, res.data)
        self.assertNotIn(serializer2.data, res.data)

    def test_retrieve_borrowing_detail(self):
        borrowing = sample_borrowing(user_id=self.user.id)

        url = detail_url(borrowing.id)
        res = self.client.get(url)

        serializer = BorrowingDetailSerializer(borrowing)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_create_borrowing(self):
        book = sample_book()

        payload = {
            "expected_return_date": "2024-02-01",
            "book": book.id,
        }

        res = self.client.post(BORROWING_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

    def test_create_borrowing_decreases_book_inventory_by_1(self):
        book = sample_book()
        expected_inventory = book.inventory - 1
        payload = {
            "expected_return_date": "2024-02-01",
            "book": book.id,
        }

        self.client.post(BORROWING_URL, payload)

        book_from_db = Book.objects.get(pk=book.id)
        actual_inventory = book_from_db.inventory

        self.assertEqual(actual_inventory, expected_inventory)

    def test_return_borrowing(self):
        borrowing = sample_borrowing(user_id=self.user.id)

        self.client.post(return_url(borrowing.id))

        instance = Borrowing.objects.get(pk=borrowing.id)
        current_date = datetime.date.today()

        self.assertEqual(instance.actual_return_date, current_date)

    def test_can_not_return_borrowing_twice(self):
        borrowing = sample_borrowing(user_id=self.user.id)

        self.client.post(return_url(borrowing.id))

        res_return_twice = self.client.post(return_url(borrowing.id))

        self.assertEqual(res_return_twice.status_code, status.HTTP_400_BAD_REQUEST)


    def test_increase_book_inventory_when_returned(self):
        borrowing = sample_borrowing(user_id=self.user.id)
        book = borrowing.book
        expected_inventory = book.inventory + 1

        self.client.post(return_url(borrowing.id))

        book_instance = Book.objects.get(pk=book.id)
        actual_inventory = book_instance.inventory

        self.assertEqual(actual_inventory, expected_inventory)


class AdminBorrowingApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "admin@admin.com", "testpass", is_staff=True
        )
        self.client.force_authenticate(self.user)

    def test_list_all_users_borrowings(self):
        another_user = sample_user()

        sample_borrowing(user_id=another_user.id)
        sample_borrowing(user_id=self.user.id)

        borrowings = Borrowing.objects.all()
        serializer = BorrowingListSerializer(borrowings, many=True)

        res = self.client.get(BORROWING_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(serializer.data, res.data)

    def test_filter_borrowings_by_user_id(self):
        test_user1 = sample_user()
        test_user2 = sample_user(email="user2@user.com")
        borrowing1 = sample_borrowing(user_id=self.user.id)
        borrowing2 = sample_borrowing(user_id=test_user1.id)
        borrowing3 = sample_borrowing(user_id=test_user2.id)

        res = self.client.get(BORROWING_URL, {"user_id": test_user1.id})

        serializer1 = BorrowingListSerializer(borrowing1)
        serializer2 = BorrowingListSerializer(borrowing2)
        serializer3 = BorrowingListSerializer(borrowing3)

        self.assertNotIn(serializer1.data, res.data)
        self.assertIn(serializer2.data, res.data)
        self.assertNotIn(serializer3.data, res.data)
