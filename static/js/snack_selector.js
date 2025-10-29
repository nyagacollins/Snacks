// Snack selection and calculation functionality

document.addEventListener('DOMContentLoaded', function() {
    const mandaziInput = document.getElementById('id_mandazi_quantity');
    const eggsInput = document.getElementById('id_eggs_quantity');
    const totalDisplay = document.getElementById('total-amount');
    
    // Get prices from data attributes
    const mandaziPrice = parseFloat(document.querySelector('[data-mandazi-price]')?.dataset.mandaziPrice || 0);
    const eggsPrice = parseFloat(document.querySelector('[data-eggs-price]')?.dataset.eggsPrice || 0);
    
    function calculateTotal() {
        const mandaziQty = parseInt(mandaziInput?.value || 0);
        const eggsQty = parseInt(eggsInput?.value || 0);
        
        const total = (mandaziQty * mandaziPrice) + (eggsQty * eggsPrice);
        
        if (totalDisplay) {
            totalDisplay.textContent = `KSh ${total.toFixed(2)}`;
        }
        
        // Update summary if exists
        updateSummary(mandaziQty, eggsQty, total);
        
        return total;
    }
    
    function updateSummary(mandaziQty, eggsQty, total) {
        const summaryElement = document.getElementById('purchase-summary');
        if (!summaryElement) return;
        
        let summaryHTML = '<h6>Purchase Summary:</h6><ul class="list-unstyled">';
        
        if (mandaziQty > 0) {
            summaryHTML += `<li><i class="fas fa-cookie-bite me-2"></i>${mandaziQty} Mandazi × KSh ${mandaziPrice} = KSh ${(mandaziQty * mandaziPrice).toFixed(2)}</li>`;
        }
        
        if (eggsQty > 0) {
            summaryHTML += `<li><i class="fas fa-egg me-2"></i>${eggsQty} Eggs × KSh ${eggsPrice} = KSh ${(eggsQty * eggsPrice).toFixed(2)}</li>`;
        }
        
        if (mandaziQty === 0 && eggsQty === 0) {
            summaryHTML += '<li class="text-muted">No items selected</li>';
        }
        
        summaryHTML += `</ul><hr><strong>Total: KSh ${total.toFixed(2)}</strong>`;
        summaryElement.innerHTML = summaryHTML;
    }
    
    // Add event listeners
    if (mandaziInput) {
        mandaziInput.addEventListener('input', calculateTotal);
        mandaziInput.addEventListener('change', calculateTotal);
    }
    
    if (eggsInput) {
        eggsInput.addEventListener('input', calculateTotal);
        eggsInput.addEventListener('change', calculateTotal);
    }
    
    // Initial calculation
    calculateTotal();
    
    // Quantity validation
    function validateQuantity(input, max) {
        const value = parseInt(input.value);
        if (value < 0) {
            input.value = 0;
        } else if (value > max) {
            input.value = max;
            showAlert(`Maximum ${max} items allowed`, 'warning');
        }
        calculateTotal();
    }
    
    if (mandaziInput) {
        mandaziInput.addEventListener('blur', function() {
            validateQuantity(this, 20);
        });
    }
    
    if (eggsInput) {
        eggsInput.addEventListener('blur', function() {
            validateQuantity(this, 10);
        });
    }
});

// Utility function to show alerts
function showAlert(message, type = 'info') {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    const container = document.querySelector('.container-fluid');
    if (container) {
        container.insertBefore(alertDiv, container.firstChild);
        
        // Auto-dismiss after 5 seconds
        setTimeout(() => {
            if (alertDiv.parentNode) {
                alertDiv.remove();
            }
        }, 5000);
    }
}