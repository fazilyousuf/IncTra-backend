from django.db import models
from django.conf import settings
from django.utils import timezone
from django.core.exceptions import ObjectDoesNotExist


class Account(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    bank = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    credit = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    food = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    entertainment = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    transportation = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    shopping = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    home = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    others = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    credit_limit = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    def _str_(self):
        return self.user


class Category(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)

    def _str_(self):
        return self.name


class Transaction(models.Model):
    INCOME = "IN"
    EXPENSE = "EX"
    TRANSACTION_TYPE_CHOICES = [
        (INCOME, "Income"),
        (EXPENSE, "Expense"),
    ]

    BANK_ACCOUNT = "bank"
    CREDIT_CARD = "credit"
    ACCOUNT_TYPE_CHOICES = [
        (BANK_ACCOUNT, "Bank Account"),
        (CREDIT_CARD, "Credit Card"),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    category = models.CharField(max_length=24)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    date = models.DateTimeField(default=timezone.now)
    description = models.TextField(blank=True, null=True)
    transaction_type = models.CharField(max_length=2, choices=TRANSACTION_TYPE_CHOICES)
    account_type = models.CharField(max_length=10, choices=ACCOUNT_TYPE_CHOICES, default='bank')

    def __str__(self):
        return f"{self.user} - {self.get_transaction_type_display()} - {self.amount}"

    def save(self, *args, **kwargs):
        is_new = self._state.adding
        super().save(*args, **kwargs)

        if is_new:
            from .models import Account  # Avoid circular import if signals used

            try:
                account, _ = Account.objects.get_or_create(user=self.user)

                if self.transaction_type == "IN":
                    if self.account_type == "bank":
                        account.bank += self.amount
                    elif self.account_type == "credit":
                        account.credit += self.amount
                elif self.transaction_type == "EX":
                    category_field = self.category.lower()
                    if hasattr(account, category_field):
                        setattr(
                            account,
                            category_field,
                            getattr(account, category_field) + self.amount,
                        )

                    if self.account_type == "bank":
                        account.bank -= self.amount
                    elif self.account_type == "credit":
                        account.credit -= self.amount

                account.save()

            except ObjectDoesNotExist:
                pass

    # Keep existing methods (save/delete logic)
