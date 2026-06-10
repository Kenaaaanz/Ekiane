import requests
from django.contrib import admin
from django.utils.html import format_html
from django.conf import settings
from django.utils import timezone
from .models import Payment


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['reference', 'order', 'amount', 'status', 'paystack_sync_status', 'created_at', 'verified_at']
    list_filter = ['status', 'created_at']
    search_fields = ['reference', 'order__email']
    readonly_fields = ['reference', 'created_at', 'verified_at', 'paystack_status_info']
    actions = ['resync_with_paystack']
    
    def paystack_sync_status(self, obj):
        """Show if payment status matches Paystack"""
        try:
            headers = {'Authorization': f'Bearer {settings.PAYSTACK_SECRET_KEY}'}
            response = requests.get(
                f'https://api.paystack.co/transaction/verify/{obj.reference}',
                headers=headers,
                timeout=5
            )
            data = response.json()
            
            if not data.get('status'):
                return format_html('<span style="color: gray;">⊘ API Error</span>')
            
            paystack_status = data['data'].get('status')
            
            if paystack_status == 'success' and obj.status != 'success':
                return format_html(
                    '<span style="color: red; font-weight: bold;">⚠ Mismatch (PS: Success)</span>'
                )
            elif paystack_status == 'failed' and obj.status != 'failed':
                return format_html(
                    '<span style="color: orange;">⚠ Mismatch (PS: Failed)</span>'
                )
            elif paystack_status == obj.status:
                return format_html('<span style="color: green;">✓ Synced</span>')
            else:
                return format_html(
                    f'<span style="color: blue;">ℹ PS: {paystack_status}</span>'
                )
        except requests.RequestException:
            return format_html('<span style="color: gray;">? No connection</span>')
        except Exception as e:
            return format_html(f'<span style="color: gray;">? Error: {str(e)[:20]}</span>')
    
    paystack_sync_status.short_description = 'Paystack Sync'
    
    def paystack_status_info(self, obj):
        """Detailed Paystack status in readonly field"""
        try:
            headers = {'Authorization': f'Bearer {settings.PAYSTACK_SECRET_KEY}'}
            response = requests.get(
                f'https://api.paystack.co/transaction/verify/{obj.reference}',
                headers=headers,
                timeout=5
            )
            data = response.json()
            
            if data.get('status') and data.get('data'):
                ps_data = data['data']
                return (
                    f"Paystack Status: {ps_data.get('status')}\n"
                    f"Amount: {ps_data.get('amount') / 100}\n"
                    f"Paid At: {ps_data.get('paid_at', 'N/A')}\n"
                    f"Gateway Response: {ps_data.get('gateway_response', 'N/A')}"
                )
            else:
                return f"Error: {data.get('message', 'Unknown error')}"
        except Exception as e:
            return f"Unable to fetch: {str(e)}"
    
    paystack_status_info.short_description = 'Paystack Info'
    
    def resync_with_paystack(self, request, queryset):
        """Action to resync selected payments with Paystack"""
        synced = 0
        failed = 0
        
        for payment in queryset:
            try:
                headers = {'Authorization': f'Bearer {settings.PAYSTACK_SECRET_KEY}'}
                response = requests.get(
                    f'https://api.paystack.co/transaction/verify/{payment.reference}',
                    headers=headers,
                    timeout=5
                )
                data = response.json()
                
                if data.get('status') and data.get('data'):
                    paystack_status = data['data'].get('status')
                    
                    if paystack_status == 'success' and payment.status != 'success':
                        payment.status = 'success'
                        payment.verified_at = timezone.now()
                        payment.save()
                        
                        order = payment.order
                        if order.status != 'paid':
                            order.paid = True
                            order.status = 'paid'
                            order.save()
                        
                        synced += 1
                    elif paystack_status == 'failed' and payment.status != 'failed':
                        payment.status = 'failed'
                        payment.save()
                        synced += 1
                else:
                    failed += 1
            except Exception as e:
                failed += 1
        
        self.message_user(
            request,
            f'Resync complete: {synced} payment(s) updated, {failed} failed.'
        )
    
    resync_with_paystack.short_description = 'Resync selected payments with Paystack'
