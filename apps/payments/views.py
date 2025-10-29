from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.utils.decorators import method_decorator
from django.db import transaction
from django.utils import timezone
from apps.accounts.decorators import buyer_required, seller_required
from .models import Consumption, Transaction
from .mpesa import MpesaAPI
import json
import logging

logger = logging.getLogger(__name__)


@login_required
@buyer_required
def payment_form(request):
    # Get consumption data from session
    consumption_data = request.session.get('consumption_data')
    if not consumption_data:
        messages.error(request, 'No consumption data found. Please select snacks first.')
        return redirect('products:select_snacks')
    
    context = {
        'consumption_data': consumption_data,
        'user_phone': request.user.phone_number
    }
    
    return render(request, 'payments/payment_form.html', context)


@login_required
@buyer_required
@require_POST
def initiate_payment(request):
    consumption_data = request.session.get('consumption_data')
    if not consumption_data:
        return JsonResponse({
            'success': False, 
            'message': 'No consumption data found. Please select snacks first.'
        })
    
    phone_number = request.POST.get('phone_number')
    if not phone_number:
        return JsonResponse({
            'success': False, 
            'message': 'Phone number is required'
        })
    
    try:
        with transaction.atomic():
            # Create consumption record
            consumption = Consumption.objects.create(
                buyer=request.user,
                mandazi_quantity=consumption_data['mandazi_quantity'],
                eggs_quantity=consumption_data['eggs_quantity'],
                mandazi_price=consumption_data['mandazi_price'],
                eggs_price=consumption_data['eggs_price'],
                total_amount=consumption_data['total_amount']
            )
            
            # Create transaction record
            transaction_record = Transaction.objects.create(
                consumption=consumption,
                buyer=request.user,
                phone_number=phone_number,
                amount=consumption_data['total_amount']
            )
            
            # Initiate M-Pesa STK Push
            mpesa = MpesaAPI()
            
            # Check M-Pesa status first
            status = mpesa.get_credentials_status()
            if not status['configured'] and not mpesa.test_mode:
                transaction_record.delete()
                consumption.delete()
                return JsonResponse({
                    'success': False,
                    'message': f'M-Pesa not configured: {status["message"]}'
                })
            
            result = mpesa.stk_push(
                phone_number=phone_number,
                amount=consumption_data['total_amount'],
                account_reference=f"SNACKS-{consumption.id}",
                transaction_desc=f"Payment for snacks - {request.user.username}"
            )
            
            if result['success']:
                transaction_record.checkout_request_id = result['checkout_request_id']
                transaction_record.save()
                
                # In test mode, simulate immediate success
                if mpesa.test_mode:
                    transaction_record.status = 'SUCCESS'
                    transaction_record.mpesa_receipt_number = f'TEST{transaction_record.id:06d}'
                    transaction_record.mpesa_transaction_id = f'TEST{transaction_record.id:08d}'
                    consumption.payment_status = 'PAID'
                    transaction_record.save()
                    consumption.save()
                
                # Clear session data
                del request.session['consumption_data']
                
                message = result['message']
                if mpesa.test_mode:
                    message += ' (Test Mode - Payment Simulated)'
                
                return JsonResponse({
                    'success': True,
                    'message': message,
                    'transaction_id': transaction_record.id,
                    'test_mode': mpesa.test_mode
                })
            else:
                # Delete records if STK push failed
                transaction_record.delete()
                consumption.delete()
                
                return JsonResponse({
                    'success': False,
                    'message': result['message']
                })
    
    except Exception as e:
        logger.error(f"Error processing payment: {e}")
        return JsonResponse({
            'success': False,
            'message': f'Error processing payment: {str(e)}'
        })


@csrf_exempt
def mpesa_callback(request):
    """Handle M-Pesa payment callback"""
    # Log all callback attempts for debugging
    logger.info(f"=== M-PESA CALLBACK RECEIVED ===")
    logger.info(f"Method: {request.method}")
    logger.info(f"Headers: {dict(request.headers)}")
    logger.info(f"Body: {request.body.decode('utf-8')}")
    logger.info(f"Remote IP: {request.META.get('REMOTE_ADDR', 'Unknown')}")
    logger.info(f"User Agent: {request.META.get('HTTP_USER_AGENT', 'Unknown')}")
    
    # Always return OK for GET requests (for testing)
    if request.method == 'GET':
        logger.info("GET request to callback - returning test response")
        return JsonResponse({
            'status': 'callback_accessible',
            'message': 'M-Pesa callback endpoint is working',
            'timestamp': timezone.now().isoformat()
        })
    
    if request.method == 'POST':
        try:
            callback_data = json.loads(request.body)
            logger.info(f"Parsed callback data: {json.dumps(callback_data, indent=2)}")
            
            # Extract callback data
            stk_callback = callback_data.get('Body', {}).get('stkCallback', {})
            checkout_request_id = stk_callback.get('CheckoutRequestID')
            result_code = stk_callback.get('ResultCode')
            result_desc = stk_callback.get('ResultDesc', '')
            
            logger.info(f"Checkout Request ID: {checkout_request_id}")
            logger.info(f"Result Code: {result_code}")
            logger.info(f"Result Description: {result_desc}")
            
            if checkout_request_id:
                try:
                    transaction_record = Transaction.objects.get(
                        checkout_request_id=checkout_request_id
                    )
                    logger.info(f"Found transaction: {transaction_record.id}")
                    
                    if result_code == 0:  # Success
                        logger.info("Payment successful - updating transaction")
                        
                        # Extract payment details
                        callback_metadata = stk_callback.get('CallbackMetadata', {}).get('Item', [])
                        logger.info(f"Callback metadata: {callback_metadata}")
                        
                        for item in callback_metadata:
                            if item.get('Name') == 'MpesaReceiptNumber':
                                transaction_record.mpesa_receipt_number = item.get('Value')
                                logger.info(f"M-Pesa Receipt: {item.get('Value')}")
                            elif item.get('Name') == 'TransactionId':
                                transaction_record.mpesa_transaction_id = item.get('Value')
                                logger.info(f"Transaction ID: {item.get('Value')}")
                        
                        transaction_record.status = 'SUCCESS'
                        transaction_record.consumption.payment_status = 'PAID'
                        
                        transaction_record.save()
                        transaction_record.consumption.save()
                        
                        logger.info("Transaction updated successfully")
                        
                    else:  # Failed
                        logger.info(f"Payment failed - Result Code: {result_code}, Description: {result_desc}")
                        transaction_record.status = 'FAILED'
                        transaction_record.consumption.payment_status = 'FAILED'
                        
                        transaction_record.save()
                        transaction_record.consumption.save()
                
                except Transaction.DoesNotExist:
                    logger.error(f"Transaction not found for checkout request ID: {checkout_request_id}")
            else:
                logger.error("No checkout request ID in callback")
            
            # Always return OK to M-Pesa
            logger.info("=== CALLBACK PROCESSED SUCCESSFULLY ===")
            return HttpResponse('OK')
        
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in callback: {e}")
            logger.error(f"Raw body: {request.body}")
            return HttpResponse('Invalid JSON', status=400)
        except Exception as e:
            logger.error(f"Error processing callback: {e}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            return HttpResponse('Error processing callback', status=500)
    
    logger.warning(f"Unsupported method: {request.method}")
    return HttpResponse('Method not allowed', status=405)


@login_required
@buyer_required
def payment_success(request, transaction_id):
    transaction_record = get_object_or_404(
        Transaction, 
        id=transaction_id, 
        buyer=request.user
    )
    
    return render(request, 'payments/payment_success.html', {
        'transaction': transaction_record
    })


@login_required
@buyer_required
def transaction_history(request):
    transactions = Transaction.objects.filter(buyer=request.user)
    return render(request, 'payments/transaction_history.html', {
        'transactions': transactions
    })


@login_required
@buyer_required
def consumption_history(request):
    consumptions = Consumption.objects.filter(buyer=request.user).order_by('-created_at')
    
    # Calculate summary statistics
    from django.db.models import Sum
    
    summary = consumptions.aggregate(
        total_mandazi=Sum('mandazi_quantity'),
        total_eggs=Sum('eggs_quantity'),
        total_spent=Sum('total_amount')
    )
    
    context = {
        'consumptions': consumptions,
        'total_mandazi': summary['total_mandazi'] or 0,
        'total_eggs': summary['total_eggs'] or 0,
        'total_spent': summary['total_spent'] or 0,
    }
    
    return render(request, 'payments/consumption_history.html', context)


@login_required
@seller_required
def all_transactions(request):
    # Get all transactions for buyers created by this seller
    transactions = Transaction.objects.filter(
        buyer__created_by=request.user
    )
    return render(request, 'payments/all_transactions.html', {
        'transactions': transactions
    })


@login_required
@seller_required
def mpesa_status(request):
    """Check M-Pesa configuration status"""
    from .mpesa import MpesaAPI
    
    mpesa = MpesaAPI()
    status = mpesa.get_credentials_status()
    
    return JsonResponse(status)


@login_required
def check_payment_status(request, transaction_id):
    """Check payment status for a transaction"""
    try:
        transaction_record = Transaction.objects.get(
            id=transaction_id,
            buyer=request.user
        )
        
        return JsonResponse({
            'status': transaction_record.status,
            'payment_status': transaction_record.consumption.payment_status,
            'mpesa_receipt': transaction_record.mpesa_receipt_number,
            'created_at': transaction_record.created_at.isoformat()
        })
    except Transaction.DoesNotExist:
        return JsonResponse({
            'status': 'NOT_FOUND',
            'message': 'Transaction not found'
        })


@login_required
@buyer_required
def manual_confirm_payment(request, transaction_id):
    """Manually confirm payment (for when callback fails)"""
    try:
        transaction_record = Transaction.objects.get(
            id=transaction_id,
            buyer=request.user,
            status='PENDING'
        )
        
        if request.method == 'POST':
            mpesa_code = request.POST.get('mpesa_code', '').strip()
            quick_confirm = request.POST.get('quick_confirm') == 'true'
            
            if mpesa_code or quick_confirm:
                # Update transaction as successful
                transaction_record.status = 'SUCCESS'
                
                if quick_confirm:
                    # For quick confirmation (testing/development)
                    transaction_record.mpesa_receipt_number = f'QUICK{transaction_record.id:06d}'
                    logger.info(f"Quick confirmation for transaction {transaction_id}")
                else:
                    # Regular manual confirmation with M-Pesa code
                    transaction_record.mpesa_receipt_number = mpesa_code
                    logger.info(f"Manual confirmation for transaction {transaction_id} with code {mpesa_code}")
                
                transaction_record.consumption.payment_status = 'PAID'
                
                transaction_record.save()
                transaction_record.consumption.save()
                
                return JsonResponse({
                    'success': True,
                    'message': 'Payment confirmed successfully!'
                })
            else:
                return JsonResponse({
                    'success': False,
                    'message': 'Please enter the M-Pesa confirmation code or use quick confirm'
                })
        
        return render(request, 'payments/manual_confirm.html', {
            'transaction': transaction_record
        })
        
    except Transaction.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'Transaction not found or already processed'
        })


@login_required
@seller_required
def callback_monitor(request):
    """Monitor callback status and recent transactions"""
    # Get recent transactions
    recent_transactions = Transaction.objects.filter(
        buyer__created_by=request.user
    ).order_by('-created_at')[:10]
    
    # Count statuses
    pending_count = Transaction.objects.filter(
        buyer__created_by=request.user,
        status='PENDING'
    ).count()
    
    success_count = Transaction.objects.filter(
        buyer__created_by=request.user,
        status='SUCCESS'
    ).count()
    
    context = {
        'recent_transactions': recent_transactions,
        'pending_count': pending_count,
        'success_count': success_count,
    }
    
    return render(request, 'payments/callback_monitor.html', context)


@login_required
@seller_required
def test_stk_push(request):
    """Test STK Push functionality"""
    if request.method == 'POST':
        phone_number = request.POST.get('phone_number')
        amount = request.POST.get('amount', 1)
        
        if not phone_number:
            return JsonResponse({
                'success': False,
                'message': 'Phone number is required'
            })
        
        from .mpesa import MpesaAPI
        mpesa = MpesaAPI()
        
        result = mpesa.stk_push(
            phone_number=phone_number,
            amount=amount,
            account_reference='TEST-STK',
            transaction_desc='Test STK Push from Snacks Payment System'
        )
        
        return JsonResponse(result)
    
    return render(request, 'payments/test_stk.html')


def test_callback(request):
    """Test endpoint to verify callback URL is accessible"""
    logger.info("Test callback endpoint accessed")
    return JsonResponse({
        'status': 'success',
        'message': 'Callback URL is accessible',
        'method': request.method,
        'timestamp': timezone.now().isoformat()
    })


@login_required
@seller_required  
def simulate_callback(request, transaction_id):
    """Simulate M-Pesa callback for testing (seller only)"""
    try:
        transaction_record = Transaction.objects.get(
            id=transaction_id,
            status='PENDING'
        )
        
        # Simulate successful callback
        transaction_record.status = 'SUCCESS'
        transaction_record.mpesa_receipt_number = f'SIM{transaction_record.id:08d}'
        transaction_record.mpesa_transaction_id = f'SIM{transaction_record.id:10d}'
        transaction_record.consumption.payment_status = 'PAID'
        
        transaction_record.save()
        transaction_record.consumption.save()
        
        logger.info(f"Simulated callback for transaction {transaction_id}")
        
        return JsonResponse({
            'success': True,
            'message': f'Simulated successful callback for transaction {transaction_id}'
        })
        
    except Transaction.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'Transaction not found or already processed'
        })