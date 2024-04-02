import random
from django.db import models
from django.contrib.auth.models import User
from django.contrib.sessions.models import Session
from decimal import Decimal

from django.core.exceptions import ValidationError
from .validators import validate_deposit_withdrawal_destination_account,validate_transfer_between_accounts


# Create your models here.

class Account(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE,related_name="account")
    account_number = models.CharField(max_length=16,unique=True, blank=True)
    balance = models.DecimalField(max_digits=12, decimal_places=2,default=0.0)
    creation_date = models.DateTimeField(auto_now_add=True)
    
    
    def generate_account_number(self):
        
        if not self.account_number:
            
            while True:
            
                account_number = ''.join(random.choices('0123456789',k=16))
                
                if not Account.objects.filter(account_number=account_number).exists():
                    
                    self.account_number = account_number
                    
                    break
                
    def save(self, *args, **kwargs) -> None:
        self.generate_account_number()
        return super().save(*args, **kwargs)
    
    def __str__(self) -> str:
        return f"{self.user}[{self.account_number}] - {self.balance}"


class TransactionType(models.TextChoices):
    DEPOSIT = 'Dépôt', 'Dépôt'
    WITHDRAWAL = 'Retrait', 'Retrait'
    TRANSFER = 'Transfert', 'Transfert'

class TransactionStatus(models.TextChoices):
    
    PENDING = 'Pending','Pending'
    SUCCESS = 'Success','Success'
    FAILED = 'Failed','Failed'


class Transaction(models.Model):
    transaction_id = models.BigIntegerField()
    source_account = models.ForeignKey(Account, related_name='source_transactions', on_delete=models.CASCADE)
    destination_account = models.ForeignKey(Account, related_name='destination_transactions',blank=True,null=True, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    TRANSACTION_TYPES = (
        ('DEPOSIT', 'Dépôt'),
        ('WITHDRAWAL', 'Retrait'),
        ('TRANSFER', 'Transfert'),
    )
    transaction_type = models.CharField(max_length=20, choices=TransactionType)
    transaction_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20,choices=TransactionStatus)  # Ex: Pending, Success, Failed
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self) -> str:
        return f"{self.transaction_type} - {self.amount} - {self.transaction_date}"
    
    def save(self, *args, **kwargs) -> None:
        self.generate_transaction_id()
        self.generate_transaction_status()
        return super().save(*args, **kwargs)
    
    def generate_transaction_id(self):
        
        """
        Generate a unique transaction ID before saving the Transaction object.
        """
        if not self.transaction_id:
            unique_id = self.generate_unique_transaction_id()
            self.transaction_id = unique_id
            
    def generate_unique_transaction_id(self):
        """
        Generate a unique transaction ID consisting of 10 digits.
        Check if the generated ID already exists in the database.
        """
        while True:
            # Generate a 10-digit random number
            unique_id = ''.join(random.choices('0123456789', k=10))
            
            # Check if the generated ID already exists in the database
            if not Transaction.objects.filter(transaction_id=unique_id).exists():
                return unique_id
    
    def clean(self):
        super().clean()
        
        # Validate that amount is positive and >= 100
        if self.amount <= 0:
            raise ValidationError("Amount must be positive.")
        elif self.amount < 100:
            raise ValidationError("Amount must be greater than or equal to 100.")
        
        if self.transaction_type == TransactionType.TRANSFER:
            validate_transfer_between_accounts(self.source_account, self.destination_account)
        else:
            validate_deposit_withdrawal_destination_account(self.destination_account)
            
    def generate_transaction_status(self):
        if self.transaction_type == TransactionType.DEPOSIT:
            self.source_account.balance += Decimal(self.amount)
            self.source_account.save()
            self.status = TransactionStatus.SUCCESS
        elif self.transaction_type == TransactionType.TRANSFER:
            if self.source_account.balance >= Decimal(self.amount):
                self.status = TransactionStatus.SUCCESS
                self.source_account.balance -= Decimal(self.amount)
                self.destination_account.balance += Decimal(self.amount)
                self.destination_account.save()
            else:
                self.status = TransactionStatus.FAILED
        elif self.transaction_type == TransactionType.WITHDRAWAL:
            if self.source_account.balance >= Decimal(self.amount):
                self.status = TransactionStatus.SUCCESS
                self.source_account.balance -= Decimal(self.amount)
                self.source_account.save()
            else:
                self.status = TransactionStatus.FAILED
        
    class Meta:
        
        ordering = ('-created_at',)

class Deposit(Transaction):
    class Meta:
        proxy = True
        ordering = ('-created_at',)

    class Manager(models.Manager):
        def get_queryset(self) -> models.QuerySet:
            return super().get_queryset().filter(transaction_type=TransactionType.DEPOSIT)

    def save(
            self, *args, **kwargs
    ):
        self.transaction_type = TransactionType.DEPOSIT
        super().save(*args, **kwargs)

    objects = Manager()


class Withdraw(Transaction):
    class Meta:
        proxy = True
        ordering = ('-created_at',)

    class Manager(models.Manager):
        def get_queryset(self) -> models.QuerySet:
            return super().get_queryset().filter(transaction_type=TransactionType.WITHDRAWAL)

    def save(
            self, *args, **kwargs
    ):
        self.transaction_type = TransactionType.WITHDRAWAL
        super().save(*args, **kwargs)

    objects = Manager()


class Transfer(Transaction):
    class Meta:
        proxy = True
        ordering = ('-created_at',)

    class Manager(models.Manager):
        def get_queryset(self) -> models.QuerySet:
            return super().get_queryset().filter(transaction_type=TransactionType.TRANSFER)

    def save(
            self, *args, **kwargs
    ):
        self.transaction_type = TransactionType.TRANSFER
        validate_transfer_between_accounts(self.source_account.account_number, self.destination_account.account_number)
        super().save(*args, **kwargs)

    objects = Manager()

class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    read = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username} - {self.message[:20]}..."
    
    class Meta:
        ordering = ('-timestamp',)


class LoginHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    login_datetime = models.DateTimeField(auto_now_add=True)
    ip_address = models.CharField(max_length=50)
    success = models.BooleanField()

    def __str__(self):
        return f"{self.user} Login at {self.login_datetime}"


class UserSession(models.Model):

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    session = models.ForeignKey(Session, on_delete=models.CASCADE)
    start_datetime = models.DateTimeField(auto_now_add=True)
    end_datetime = models.DateTimeField(null=True, blank=True)
    ip_address = models.CharField(max_length=50)
    ACTIVE_STATUS = 'Active'
    EXPIRED_STATUS = 'Expired'
    SESSION_STATUS_CHOICES = [
        (ACTIVE_STATUS, 'Active'),
        (EXPIRED_STATUS, 'Expired'),
    ]
    status = models.CharField(max_length=10, choices=SESSION_STATUS_CHOICES, default=ACTIVE_STATUS)

    def __str__(self):
        return f"{self.user} Session {self.status}  [{self.start_datetime}-{self.end_datetime}]"

