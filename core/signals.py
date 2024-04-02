import random
from django.dispatch import receiver
from django.db.models.signals import post_save,pre_save

from django.contrib.auth import get_user_model

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

from .models import Account,Notification,TransactionType,TransactionStatus,Transfer,Withdraw,Deposit

User = get_user_model()


@receiver(post_save,sender=User)
def create_account(sender,instance,created,**kwargs):
    
    if created:
        
        Account.objects.create(user=instance,balance=0.0)


@receiver(post_save, sender=Transfer)
def send_transfer_notification(sender, instance: Transfer, created, **kwargs):
    if not created:
        return  # Ignore updates to existing transactions
    
    if instance.transaction_type == TransactionType.TRANSFER and instance.status == TransactionStatus.SUCCESS:
        if instance.destination_account.user != instance.source_account.user:
            # Sender notification
            sender_message = f"Your transfer of {instance.amount} XAF to {instance.destination_account.user.username} was successful at {instance.created_at}, transaction Id: {instance.transaction_id}, new account balance: {instance.source_account.balance}."
            Notification.objects.create(user=instance.source_account.user, message=sender_message)
            # Receiver notification
            receiver_message = f"You received a transfer of {instance.amount} XAF from {instance.source_account.user.username}, transaction Id: {instance.transaction_id}, new account balance: {instance.destination_account.balance}."
            Notification.objects.create(user=instance.destination_account.user, message=receiver_message)

# Signal handler for failed transfers
@receiver(post_save, sender=Transfer)
def send_failed_transfer_notification(sender, instance: Transfer, created, **kwargs):
    if not created:
        return  # Ignore updates to existing transactions
    
    if instance.transaction_type == TransactionType.TRANSFER and instance.status == TransactionStatus.FAILED:
        if instance.destination_account.user != instance.source_account.user:
            message = f"Transaction of {instance.amount} XAF to {instance.destination_account.user.username} failed due to insufficient balance."
            Notification.objects.create(user=instance.source_account.user, message=message)

# Signal handler for successful deposits
@receiver(post_save, sender=Deposit)
def send_deposit_notification(sender, instance: Deposit, created, **kwargs):
    print("Deposit")
    
    if not created:
        return  # Ignore updates to existing transactions
    
    if instance.transaction_type == TransactionType.DEPOSIT and instance.status == TransactionStatus.SUCCESS:
        message = f"You received a deposit of {instance.amount} XAF from {instance.source_account.user.username} at {instance.created_at}, transaction Id: {instance.transaction_id}, new account balance: {instance.source_account.balance}."
        Notification.objects.create(user=instance.source_account.user, message=message)

# Signal handler for successful withdrawals
@receiver(post_save, sender=Withdraw)
def send_withdrawal_notification(sender, instance: Withdraw, created, **kwargs):
    print("Withdraw")
    if not created:
        return  # Ignore updates to existing transactions
    
    if instance.transaction_type == TransactionType.WITHDRAWAL and instance.status == TransactionStatus.SUCCESS:
        message = f"Your withdrawal of {instance.amount} XAF was successful at {instance.created_at}, transaction Id: {instance.transaction_id}, new account balance: {instance.source_account.balance}."
        Notification.objects.create(user=instance.source_account.user, message=message)
        
# Send Notification through channel 

# @receiver(post_save, sender=Notification)
# def send_notification(sender, instance, created, **kwargs):
#     from django.core.serializers import serialize
#     if created:
#         # Get the user associated with the notification
#         user = instance.user
        
#         channel_layer = get_channel_layer()
        
#         DATA = {
#             "message": instance.message,
#             "timestamp": instance.timestamp,
#         }
        
#         # Send notification through WebSocket
#         async_to_sync(channel_layer.group_send)(
#             f"notifications_{user.id}",
#             {
#                 "type": "send_notification",
#                 "notification": DATA
#             }
#         )