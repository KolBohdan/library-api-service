import datetime

from django.db import transaction
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from book.serializers import BookSerializer
from borrowing.models import Borrowing
from telegram_helper.bot import send_create_notification


class BorrowingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Borrowing
        fields = (
            "id",
            "borrow_date",
            "expected_return_date",
            "actual_return_date",
            "book",
            "user",
            "is_active",
        )
        read_only_fields = fields


class BorrowingListSerializer(BorrowingSerializer):
    book_title = serializers.CharField(source="book.title", read_only=True)

    class Meta:
        model = Borrowing
        fields = ("id", "book_title", "expected_return_date", "user", "is_active")
        read_only_fields = fields


class BorrowingDetailSerializer(BorrowingSerializer):
    book = BookSerializer(many=False, read_only=True)

    def validate(self, attrs):
        data = super(BorrowingDetailSerializer, self).validate(attrs=attrs)

        if self.instance.actual_return_date:
            raise serializers.ValidationError("You have already returned this book.")

        return data

    def update(self, instance, validated_data):
        with transaction.atomic():
            book = instance.book
            book.increase_inventory_when_returned()

            instance.actual_return_date = datetime.date.today()
            instance.save()

            return instance


class BorrowingCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Borrowing
        fields = ("id", "book", "borrow_date", "expected_return_date")

    def validate(self, attrs):
        data = super(BorrowingCreateSerializer, self).validate(attrs=attrs)
        Borrowing.validate_book_inventory(
            attrs["book"],
            ValidationError,
        )
        return data

    def create(self, validated_data):
        with transaction.atomic():
            borrowing = Borrowing.objects.create(**validated_data)

            book = validated_data.get("book")

            book.decrease_inventory_when_borrowed()

            message_to_send = (
                "Borrowing Created\n"
                f"\nBorrowing Date: {borrowing.borrow_date}\n"
                f"Expected Return Date: {borrowing.expected_return_date}\n"
                f"Book Title: {book.title}\n"
                f"Book Author: {book.author}\n"
                f"Daily Fee: {book.daily_fee}\n"
            )
            send_create_notification(message_to_send)

            return borrowing
