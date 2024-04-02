from django import forms
from .models import Transaction,Account,Transfer
from django.contrib.auth import get_user_model
import re

from django.contrib.auth.forms import AuthenticationForm,PasswordChangeForm,UserCreationForm

User = get_user_model()

class UserChangeForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email'] 


class LoginForm(forms.Form):
    
    INPUT_CLASSS = "flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
    
    username = forms.CharField(max_length=120,min_length=3,widget=forms.TextInput(attrs={'class':INPUT_CLASSS}))
    password = forms.CharField(max_length=255,widget=forms.PasswordInput(attrs={'class':INPUT_CLASSS}))
    
    
class DepositForm(forms.ModelForm):
    
    amount = forms.DecimalField(min_value=100)
    
    
    class Meta:
        
        model = Transaction
        fields = ['amount']
        

class WithdrawForm(forms.ModelForm):
    
    amount = forms.DecimalField(min_value=100)
    
    
    class Meta:
        
        model = Transaction
        fields = ['amount']
        
class TransferForm(forms.ModelForm):
    current_user_account_number = forms.CharField(max_length=16, min_length=16, required=True, help_text="Use the IBAN of the receiver for the transaction",widget=forms.HiddenInput())
    reciepient_account_number = forms.CharField(max_length=19, min_length=19, required=True, help_text="Use the IBAN of the receiver for the transaction")
    amount = forms.DecimalField(min_value=100)
    
    class Meta:
        model = Transfer
        fields = ['reciepient_account_number', 'amount','current_user_account_number']

    def clean_reciepient_account_number(self):
        # Retrieve cleaned data for the recipient account number field
        reciepient_account_number = self.cleaned_data.get('reciepient_account_number')
        
        # You can perform additional validation or cleaning here if needed
        
        reciepient_account_number = str(reciepient_account_number).replace(' ','')

        
        
        if not Account.objects.filter(account_number=reciepient_account_number).exists():
            raise forms.ValidationError("This account number does not exist")
        
        
        # Return the cleaned data
        return reciepient_account_number
    
    def clean(self):
        cleaned_data = super().clean()
        
        current_user_account_number = cleaned_data.get('current_user_account_number')
        reciepient_account_number = str(cleaned_data.get('reciepient_account_number')).replace(' ','')
        
        # if current_user_account_number == reciepient_account_number:
        #     print("current_user_account_number == reciepient_account_number")
        #     raise forms.ValidationError("You Can't Transfer money to your self!")
        
        if current_user_account_number == reciepient_account_number:
            self.add_error('reciepient_account_number', forms.ValidationError("You can't transfer money to yourself!"))
        
        return cleaned_data