from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import CheckConstraint, Q, F

from book.models import Book


class Borrowing(models.Model):
    borrow_date = models.DateField(auto_now_add=True)
    expected_return_date = models.DateField()
    actual_return_date = models.DateField(null=True, blank=True)
    book = models.ForeignKey(
        to=Book, on_delete=models.CASCADE, related_name="borrowings"
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="borrowings"
    )

    class Meta:
        ordering = ["-borrow_date"]
        constraints = [
            CheckConstraint(
                check=(
                    Q(borrow_date__lte=F("expected_return_date"))
                    & Q(borrow_date__lte=F("actual_return_date"))
                ),
                name="borrow_date_lte_return_date",
            ),
        ]

    @staticmethod
    def validate_book_inventory(book, error_to_raise):
        if book.inventory <= 0:
            raise error_to_raise(
                {
                    "book_inventory": f"{book.title} is currently out of stock"
                }
            )

    def clean(self):
        Borrowing.validate_book_inventory(
            self.book,
            ValidationError,
        )

    def save(
        self,
        force_insert=False,
        force_update=False,
        using=None,
        update_fields=None,
    ):
        self.full_clean()
        return super(Borrowing, self).save(
            force_insert, force_update, using, update_fields
        )

    def __str__(self) -> str:
        return f"{self.book} borrowed by {self.user} at {str(self.borrow_date)}"
