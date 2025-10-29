// Payment processing functionality

document.addEventListener('DOMContentLoaded', function() {
    const paymentForm = document.getElementById('payment-form');
    const phoneInput = document.getElementById('phone-number');
    const submitBtn = document.getElementById('submit-payment');
    
    if (paymentForm) {
        paymentForm.addEventListener('submit', function(e) {
            e.preventDefault();
            initiatePayment();
        });
    }
    
    // Phone number formatting
    if (phoneInput) {
        phoneInput.addEventListener('input', function() {
            formatPhoneNumber(this);
        });
    }
});

function formatPhoneNumber(input) {
    let value = input.value.replace(/\D/g, ''); // Remove non-digits
    
    // Handle different formats
    if (value.startsWith('254')) {
        // Already in international format
        input.value = '+' + value;
    } else if (value.startsWith('0')) {
        // Local format, convert to international
        input.value = '+254' + value.substring(1);
    } else if (value.length > 0) {
        // Assume it's missing the country code
        input.value = '+254' + value;
    }
}

function initiatePayment() {
    const submitBtn = document.getElementById('submit-payment');
    const phoneNumber = document.getElementById('phone-number').value;
    
    if (!phoneNumber) {
        showAlert('Please enter your phone number', 'danger');
        return;
    }
    
    // Validate phone number format
    const phoneRegex = /^\+254[17]\d{8}$/;
    if (!phoneRegex.test(phoneNumber)) {
        showAlert('Please enter a valid Kenyan phone number (e.g., +254712345678)', 'danger');
        return;
    }
    
    // Disable button and show loading
    submitBtn.disabled = true;
    submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Processing...';
    
    // Prepare form data
    const formData = new FormData();
    formData.append('phone_number', phoneNumber);
    formData.append('csrfmiddlewaretoken', document.querySelector('[name=csrfmiddlewaretoken]').value);
    
    // Send payment request
    fetch('/payments/initiate-payment/', {
        method: 'POST',
        body: formData,
        headers: {
            'X-Requested-With': 'XMLHttpRequest'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            let message = data.message || 'Payment request sent successfully!';
            
            if (data.test_mode) {
                showAlert(message + ' 🧪', 'info');
                // In test mode, redirect immediately to success page
                setTimeout(() => {
                    window.location.href = `/payments/success/${data.transaction_id}/`;
                }, 2000);
            } else {
                showAlert(message + ' Please check your phone and enter your M-Pesa PIN.', 'success');
                
                // Show payment status section
                const statusSection = document.getElementById('payment-status');
                if (statusSection) {
                    statusSection.style.display = 'block';
                }
                
                // Show manual confirmation option after 10 seconds (much sooner)
                setTimeout(() => {
                    const manualSection = document.getElementById('manual-section');
                    const manualConfirmBtn = document.getElementById('manual-confirm-btn');
                    const statusSubtitle = document.getElementById('status-subtitle');
                    
                    if (manualSection) {
                        manualSection.style.display = 'block';
                    }
                    
                    if (manualConfirmBtn) {
                        manualConfirmBtn.href = `/payments/manual-confirm/${data.transaction_id}/`;
                    }
                    
                    if (statusSubtitle) {
                        statusSubtitle.innerHTML = 'Waiting for automatic confirmation... <br><small class="text-warning">Or use manual confirmation below if you\'ve completed payment</small>';
                    }
                }, 10000); // Show after just 10 seconds
                
                // Show additional options after 30 seconds
                setTimeout(() => {
                    const autoButtons = document.getElementById('auto-buttons');
                    const manualCheckBtn = document.getElementById('manual-check-btn');
                    
                    if (autoButtons) {
                        autoButtons.style.display = 'flex';
                    }
                    
                    if (manualCheckBtn) {
                        manualCheckBtn.onclick = () => checkPaymentStatus(data.transaction_id, 0);
                    }
                }, 30000);
                
                // Start checking payment status for real payments
                if (data.transaction_id) {
                    checkPaymentStatus(data.transaction_id);
                }
            }
        } else {
            showAlert(data.message || 'Payment failed. Please try again.', 'danger');
            resetSubmitButton();
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showAlert('Network error. Please check your connection and try again.', 'danger');
        resetSubmitButton();
    });
}

function resetSubmitButton() {
    const submitBtn = document.getElementById('submit-payment');
    if (submitBtn) {
        submitBtn.disabled = false;
        submitBtn.innerHTML = '<i class="fas fa-mobile-alt me-2"></i>Send Payment Request';
    }
}

function checkPaymentStatus(transactionId, attempts = 0) {
    const maxAttempts = 20; // Check for 2 minutes (20 * 6 seconds) - reduced time
    
    if (attempts >= maxAttempts) {
        // Stop automatic checking and encourage manual confirmation
        const statusMessage = document.getElementById('status-message');
        const loadingSpinner = document.getElementById('loading-spinner');
        
        if (statusMessage) {
            statusMessage.innerHTML = 'Automatic confirmation timed out';
            statusMessage.className = 'fw-bold text-warning mb-2';
        }
        
        if (loadingSpinner) {
            loadingSpinner.style.display = 'none';
        }
        
        showAlert(`
            <strong>Payment confirmation timed out.</strong><br>
            If you completed the M-Pesa payment, 
            <a href="/payments/manual-confirm/${transactionId}/" class="alert-link fw-bold">click here to confirm manually</a>.
        `, 'warning');
        
        return; // Don't reset button, let user use manual confirmation
    }
    
    // Show status message with countdown
    const timeLeft = maxAttempts - attempts;
    updatePaymentStatus(`Waiting for automatic confirmation... (${timeLeft} checks remaining)`);
    
    setTimeout(() => {
        fetch(`/payments/check-status/${transactionId}/`, {
            headers: {
                'X-Requested-With': 'XMLHttpRequest'
            }
        })
        .then(response => response.json())
        .then(data => {
            console.log('Payment status check:', data);
            
            if (data.status === 'SUCCESS' && data.payment_status === 'PAID') {
                showAlert('Payment successful! 🎉 Redirecting...', 'success');
                setTimeout(() => {
                    window.location.href = `/payments/success/${transactionId}/`;
                }, 1500);
            } else if (data.status === 'FAILED') {
                showAlert('Payment failed. Please try again.', 'danger');
                resetSubmitButton();
            } else if (data.status === 'NOT_FOUND') {
                showAlert('Transaction not found. Please try again.', 'danger');
                resetSubmitButton();
            } else {
                // Still pending, check again
                checkPaymentStatus(transactionId, attempts + 1);
            }
        })
        .catch(error => {
            console.error('Status check error:', error);
            // Continue checking even if there's an error
            checkPaymentStatus(transactionId, attempts + 1);
        });
    }, 6000); // Check every 6 seconds
}

function updatePaymentStatus(message) {
    const statusElement = document.getElementById('status-message');
    if (statusElement) {
        statusElement.textContent = message;
    }
}

function showAlert(message, type = 'info') {
    // Remove existing alerts
    const existingAlerts = document.querySelectorAll('.alert');
    existingAlerts.forEach(alert => alert.remove());
    
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    const container = document.querySelector('.container-fluid');
    if (container) {
        container.insertBefore(alertDiv, container.firstChild);
        
        // Auto-dismiss success/info alerts after 5 seconds
        if (type === 'success' || type === 'info') {
            setTimeout(() => {
                if (alertDiv.parentNode) {
                    alertDiv.remove();
                }
            }, 5000);
        }
    }
}

// Add payment status checking for existing transactions
function initializePaymentStatusCheck() {
    const transactionId = document.querySelector('[data-transaction-id]')?.dataset.transactionId;
    if (transactionId) {
        checkPaymentStatus(transactionId);
    }
}