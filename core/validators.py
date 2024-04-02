from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _



def validate_deposit_withdrawal_destination_account(value):
    if value is not None:
        raise ValidationError(
            _('For deposit or withdrawal transactions, destination account should be None.'),
            params={'value': value},
        )

def validate_transfer_between_accounts(source_account, destination_account):
    if source_account == destination_account:
        raise ValidationError(
            _('Source account and destination account should be different for transfer transactions.'),
            params={'source_account': source_account, 'destination_account': destination_account},
        )