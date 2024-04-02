from django.contrib import admin

# Register your models here.

from .models import Account,LoginHistory,Transaction,UserSession,Notification
from core.templatetags.custom_filters import format_account_number

@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    
    list_display = ('id','user','bank_account_number','balance')
    search_fields = ('account_number','user__username')
    
    def bank_account_number(self,obj):
        return format_account_number(obj.account_number)

@admin.register(Transaction)    
class TransactionAdmin(admin.ModelAdmin):
    
    readonly_fields = ['status','transaction_id']
    
    
    list_display = ('id','source_account','destination_account','amount','transaction_type','transaction_date','status')
    search_fields = ('status','source_account','destination_account',)
    list_filter = ('status','transaction_type','transaction_date')
    
    
    
@admin.register(UserSession)
class UserSessionAdmin(admin.ModelAdmin):
    
    list_display = ('id','user','start_datetime','end_datetime','ip_address','status')
    search_fields = ('user__username',)
    
    list_filter = ('ip_address',)
    
@admin.register(LoginHistory)
class LoginHistoryAdmin(admin.ModelAdmin):
    
    list_display = ('id','user','login_datetime','ip_address','success')

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    
    list_display = ('id','user','message')