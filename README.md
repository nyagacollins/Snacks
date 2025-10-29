# Snacks Payment System

A Django-based web application for managing snack sales (Mandazi and Eggs) with integrated M-Pesa payment functionality.

## Features

### For Buyers
- Login to personal account
- Select snacks taken (Mandazi & Eggs) with quantities
- View automatic total calculation
- Make payments via M-Pesa STK Push
- Edit phone number before payment
- View personal transaction history
- Track consumption history

### For Sellers
- Register and manage buyers
- Set/update prices for Mandazi and Eggs
- View all incoming transactions in real-time
- Access daily sales reports
- View individual buyer transaction and consumption history
- Receive payments directly to M-Pesa Paybill account

## Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd snacks_payment_system
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Setup MySQL Database**
   - Create a MySQL database named `snacks_payment_db`
   - Update database credentials in `.env` file

5. **Configure Environment Variables**
   - Copy `.env` file and update with your settings:
   ```env
   SECRET_KEY=your-secret-key-here
   DEBUG=True
   
   # Database
   DB_NAME=snacks_payment_db
   DB_USER=root
   DB_PASSWORD=your-password
   DB_HOST=localhost
   DB_PORT=3306
   
   # M-Pesa Daraja API
   MPESA_CONSUMER_KEY=your-consumer-key
   MPESA_CONSUMER_SECRET=your-consumer-secret
   MPESA_SHORTCODE=your-shortcode
   MPESA_PASSKEY=your-passkey
   MPESA_CALLBACK_URL=https://yourdomain.com/payments/callback/
   MPESA_ENVIRONMENT=sandbox
   ```

6. **Run Migrations**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

7. **Create Superuser**
   ```bash
   python manage.py createsuperuser
   ```

8. **Create Initial Products**
   ```bash
   python manage.py shell
   ```
   ```python
   from apps.products.models import Product
   Product.objects.create(name='MANDAZI', price=10.00, description='Fresh mandazi')
   Product.objects.create(name='EGGS', price=15.00, description='Boiled eggs')
   ```

9. **Run Development Server**
   ```bash
   python manage.py runserver
   ```

## M-Pesa Integration Setup

1. **Register for Daraja API**
   - Visit [Safaricom Daraja](https://developer.safaricom.co.ke/)
   - Create an app and get Consumer Key and Secret
   - Get your Paybill/Till number and Passkey

2. **Configure Callback URL**
   - Set up a public URL for callbacks (use ngrok for development)
   - Update `MPESA_CALLBACK_URL` in your `.env` file

3. **Test in Sandbox**
   - Use sandbox environment for testing
   - Use test phone numbers provided by Safaricom

## Usage

### Seller Workflow
1. Login as seller
2. Register buyers with their details
3. Set/update product prices
4. Monitor transactions in real-time
5. Generate daily/monthly reports

### Buyer Workflow
1. Receive snacks from seller (physical)
2. Login to buyer account
3. Select quantities of consumed snacks
4. Make payment via M-Pesa
5. Receive confirmation

## Project Structure

```
snacks_payment_system/
├── manage.py
├── requirements.txt
├── .env
├── config/                 # Django settings
├── apps/
│   ├── accounts/          # User management
│   ├── products/          # Snacks management
│   ├── payments/          # M-Pesa integration
│   └── reports/           # Analytics
├── static/                # CSS, JS, Images
└── templates/             # HTML templates
```

## Security Features

- Django session-based authentication
- Role-based access control
- CSRF protection
- Password hashing (PBKDF2)
- M-Pesa credentials in environment variables
- HTTPS required for production
- Callback validation
- User data isolation

## API Endpoints

- `/accounts/login/` - User login
- `/products/select-snacks/` - Snack selection
- `/payments/initiate-payment/` - Start M-Pesa payment
- `/payments/callback/` - M-Pesa callback handler
- `/reports/daily-sales/` - Daily sales report

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License.

## Support

For support, please contact the development team or create an issue in the repository.