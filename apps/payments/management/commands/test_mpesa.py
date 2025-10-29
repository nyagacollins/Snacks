from django.core.management.base import BaseCommand
from apps.payments.mpesa import MpesaAPI


class Command(BaseCommand):
    help = 'Test M-Pesa API connection and STK Push functionality'

    def add_arguments(self, parser):
        parser.add_argument(
            '--phone',
            type=str,
            help='Phone number to test STK Push (format: +254XXXXXXXXX or 07XXXXXXXX)',
        )
        parser.add_argument(
            '--amount',
            type=float,
            default=1.0,
            help='Amount to test (default: 1.0)',
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Testing M-Pesa API Connection...'))
        
        mpesa = MpesaAPI()
        
        # Test 1: Check credentials status
        self.stdout.write('\n1. Checking M-Pesa credentials...')
        status = mpesa.get_credentials_status()
        
        if status['status'] == 'test_mode':
            self.stdout.write(self.style.WARNING(f"   Status: {status['message']}"))
        elif status['configured']:
            self.stdout.write(self.style.SUCCESS(f"   Status: {status['message']}"))
        else:
            self.stdout.write(self.style.ERROR(f"   Status: {status['message']}"))
            return
        
        # Test 2: Get access token
        self.stdout.write('\n2. Testing access token...')
        access_token = mpesa.get_access_token()
        
        if access_token:
            if mpesa.test_mode:
                self.stdout.write(self.style.WARNING('   Access token: Mock token (test mode)'))
            else:
                self.stdout.write(self.style.SUCCESS(f'   Access token: {access_token[:20]}...'))
        else:
            self.stdout.write(self.style.ERROR('   Failed to get access token'))
            return
        
        # Test 3: STK Push (if phone number provided)
        phone_number = options.get('phone')
        if phone_number:
            self.stdout.write(f'\n3. Testing STK Push to {phone_number}...')
            
            result = mpesa.stk_push(
                phone_number=phone_number,
                amount=options['amount'],
                account_reference='TEST-PAYMENT',
                transaction_desc='Test payment from Snacks Payment System'
            )
            
            if result['success']:
                self.stdout.write(self.style.SUCCESS(f"   STK Push sent successfully!"))
                self.stdout.write(f"   Message: {result['message']}")
                self.stdout.write(f"   Checkout Request ID: {result['checkout_request_id']}")
                
                if not mpesa.test_mode:
                    self.stdout.write(self.style.WARNING(
                        f"\n   📱 Check phone {phone_number} for M-Pesa prompt!"
                    ))
            else:
                self.stdout.write(self.style.ERROR(f"   STK Push failed: {result['message']}"))
        else:
            self.stdout.write('\n3. Skipping STK Push test (no phone number provided)')
            self.stdout.write('   Use --phone +254XXXXXXXXX to test STK Push')
        
        # Summary
        self.stdout.write('\n' + '='*50)
        if mpesa.test_mode:
            self.stdout.write(self.style.WARNING('SUMMARY: Running in TEST MODE'))
            self.stdout.write('- No real STK pushes will be sent')
            self.stdout.write('- Set MPESA_TEST_MODE=false in .env for real payments')
        else:
            self.stdout.write(self.style.SUCCESS('SUMMARY: M-Pesa is configured for REAL payments'))
            self.stdout.write('- STK pushes will be sent to actual phone numbers')
            self.stdout.write('- Make sure your callback URL is accessible')
        
        self.stdout.write('\nConfiguration:')
        self.stdout.write(f'- Environment: {mpesa.environment}')
        self.stdout.write(f'- Shortcode: {mpesa.shortcode}')
        self.stdout.write(f'- Callback URL: {mpesa.callback_url}')
        self.stdout.write(f'- Test Mode: {mpesa.test_mode}')