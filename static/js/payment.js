// Payment Form JavaScript for PaySecure

document.addEventListener('DOMContentLoaded', function() {
    // Initialize payment form
    initPaymentForm();
    
    // Initialize card preview
    initCardPreview();
    
    // Initialize payment processing
    initPaymentProcessing();
    
    // Initialize amount calculator
    initAmountCalculator();
});

// Payment Form Initialization
function initPaymentForm() {
    const form = document.getElementById('payment-form');
    if (!form) return;
    
    // Real-time validation
    const inputs = form.querySelectorAll('input');
    inputs.forEach(input => {
        input.addEventListener('input', debounce(function() {
            validatePaymentField(this);
        }, 300));
        
        input.addEventListener('blur', function() {
            validatePaymentField(this);
        });
        
        input.addEventListener('focus', function() {
            clearFieldError(this);
        });
    });
    
    // Form submission
    form.addEventListener('submit', handlePaymentSubmission);
    
    // Card number formatting
    const cardNumberInput = document.getElementById('card_number');
    if (cardNumberInput) {
        cardNumberInput.addEventListener('input', formatCardNumber);
        cardNumberInput.addEventListener('input', detectCardType);
    }
    
    // Expiry date formatting
    const expiryInput = document.getElementById('expiry_date');
    if (expiryInput) {
        expiryInput.addEventListener('input', formatExpiryDate);
    }
    
    // CVV validation
    const cvvInput = document.getElementById('cvv');
    if (cvvInput) {
        cvvInput.addEventListener('input', validateCVV);
    }
    
    // Amount formatting
    const amountInput = document.getElementById('amount');
    if (amountInput) {
        amountInput.addEventListener('input', formatAmount);
    }
}

// Card Preview Initialization
function initCardPreview() {
    const cardNumberInput = document.getElementById('card_number');
    const nameInput = document.getElementById('full_name');
    const expiryInput = document.getElementById('expiry_date');
    
    if (cardNumberInput) {
        cardNumberInput.addEventListener('input', updateCardPreview);
    }
    
    if (nameInput) {
        nameInput.addEventListener('input', updateCardPreview);
    }
    
    if (expiryInput) {
        expiryInput.addEventListener('input', updateCardPreview);
    }
    
    // Initialize card preview animation
    animateCardPreview();
}

// Update Card Preview
function updateCardPreview() {
    const cardNumber = document.getElementById('card_number').value || '';
    const name = document.getElementById('full_name').value || 'NOMBRE COMPLETO';
    const expiry = document.getElementById('expiry_date').value || 'MM/AA';
    
    // Update card number
    const previewNumber = document.getElementById('preview-number');
    if (previewNumber) {
        const maskedNumber = cardNumber || '**** **** **** ****';
        previewNumber.textContent = maskedNumber;
    }
    
    // Update cardholder name
    const previewName = document.getElementById('preview-name');
    if (previewName) {
        previewName.textContent = name.toUpperCase();
    }
    
    // Update expiry date
    const previewExpiry = document.getElementById('preview-expiry');
    if (previewExpiry) {
        previewExpiry.textContent = expiry;
    }
    
    // Update card brand logo
    updateCardBrand(cardNumber);
}

// Format Card Number
function formatCardNumber(event) {
    let value = event.target.value.replace(/\s/g, '');
    let formattedValue = '';
    
    for (let i = 0; i < value.length; i++) {
        if (i > 0 && i % 4 === 0) {
            formattedValue += ' ';
        }
        formattedValue += value[i];
    }
    
    event.target.value = formattedValue;
}

// Detect Card Type
function detectCardType(event) {
    const cardNumber = event.target.value.replace(/\s/g, '');
    const cardIcon = document.getElementById('card-icon');
    const previewLogo = document.getElementById('preview-logo');
    
    let cardType = 'default';
    let brand = '';
    
    if (cardNumber.startsWith('4')) {
        cardType = 'visa';
        brand = '<i class="fab fa-cc-visa text-white text-2xl"></i>';
    } else if (cardNumber.startsWith('5') || cardNumber.startsWith('2')) {
        cardType = 'mastercard';
        brand = '<i class="fab fa-cc-mastercard text-white text-2xl"></i>';
    } else if (cardNumber.startsWith('3')) {
        cardType = 'amex';
        brand = '<i class="fab fa-cc-amex text-white text-2xl"></i>';
    } else if (cardNumber.startsWith('6')) {
        cardType = 'discover';
        brand = '<i class="fab fa-cc-discover text-white text-2xl"></i>';
    }
    
    // Update icons
    if (cardIcon) {
        switch (cardType) {
            case 'visa':
                cardIcon.className = 'fab fa-cc-visa text-blue-600 text-xl';
                break;
            case 'mastercard':
                cardIcon.className = 'fab fa-cc-mastercard text-red-600 text-xl';
                break;
            case 'amex':
                cardIcon.className = 'fab fa-cc-amex text-blue-700 text-xl';
                break;
            default:
                cardIcon.className = 'fas fa-credit-card text-gray-400';
        }
    }
    
    if (previewLogo) {
        previewLogo.innerHTML = brand || '<i class="fas fa-credit-card text-white text-2xl"></i>';
    }
}

// Update Card Brand
function updateCardBrand(cardNumber) {
    const cardPreview = document.getElementById('card-preview');
    if (!cardPreview) return;
    
    // Change card color based on brand
    if (cardNumber.startsWith('4')) {
        cardPreview.querySelector('.card-front').style.background = 
            'linear-gradient(135deg, #1e3c72 0%, #2a5298 100%)';
    } else if (cardNumber.startsWith('5') || cardNumber.startsWith('2')) {
        cardPreview.querySelector('.card-front').style.background = 
            'linear-gradient(135deg, #eb3349 0%, #f45c43 100%)';
    } else if (cardNumber.startsWith('3')) {
        cardPreview.querySelector('.card-front').style.background = 
            'linear-gradient(135deg, #2E8B57 0%, #3CB371 100%)';
    } else {
        cardPreview.querySelector('.card-front').style.background = 
            'linear-gradient(135deg, #667eea 0%, #764ba2 100%)';
    }
}

// Format Expiry Date
function formatExpiryDate(event) {
    let value = event.target.value.replace(/\D/g, '');
    let formattedValue = '';
    
    if (value.length >= 2) {
        formattedValue = value.substring(0, 2) + '/' + value.substring(2, 4);
    } else {
        formattedValue = value;
    }
    
    event.target.value = formattedValue;
}

// Validate CVV
function validateCVV(event) {
    const value = event.target.value.replace(/\D/g, '');
    event.target.value = value;
}

// Format Amount
function formatAmount(event) {
    let value = event.target.value.replace(/[^\d.]/g, '');
    
    // Ensure only one decimal point
    const parts = value.split('.');
    if (parts.length > 2) {
        value = parts[0] + '.' + parts.slice(1).join('');
    }
    
    // Limit to 2 decimal places
    if (parts[1] && parts[1].length > 2) {
        value = parts[0] + '.' + parts[1].substring(0, 2);
    }
    
    event.target.value = value;
}

// Amount Calculator
function initAmountCalculator() {
    const amountInput = document.getElementById('amount');
    if (amountInput) {
        amountInput.addEventListener('input', updatePaymentSummary);
    }
}

// Update Payment Summary
function updatePaymentSummary() {
    const amount = parseFloat(document.getElementById('amount').value) || 0;
    const fee = amount * 0.029;
    const total = amount + fee;
    
    // Update summary display
    const subtotalElement = document.getElementById('summary-subtotal');
    const feeElement = document.getElementById('summary-fee');
    const totalElement = document.getElementById('summary-total');
    
    if (subtotalElement) subtotalElement.textContent = `$${amount.toFixed(2)}`;
    if (feeElement) feeElement.textContent = `$${fee.toFixed(2)}`;
    if (totalElement) totalElement.textContent = `$${total.toFixed(2)}`;
}

// Payment Field Validation
function validatePaymentField(field) {
    const value = field.value.trim();
    const fieldName = field.name || field.id;
    let isValid = true;
    let errorMessage = '';
    
    // Required validation
    if (field.hasAttribute('required') && !value) {
        isValid = false;
        errorMessage = 'Este campo es requerido';
    }
    
    // Specific validations
    switch (fieldName) {
        case 'full_name':
            if (value && value.length < 3) {
                isValid = false;
                errorMessage = 'El nombre debe tener al menos 3 caracteres';
            }
            break;
            
        case 'rfc':
            if (value && !isValidRFC(value)) {
                isValid = false;
                errorMessage = 'RFC inválido (debe tener 12 o 13 caracteres)';
            }
            break;
            
        case 'card_number':
            const cardNumber = value.replace(/\s/g, '');
            if (value && !isValidCardNumber(cardNumber)) {
                isValid = false;
                errorMessage = 'Número de tarjeta inválido';
            }
            break;
            
        case 'expiry_date':
            if (value && !isValidExpiryDate(value)) {
                isValid = false;
                errorMessage = 'Fecha de expiración inválida o tarjeta expirada';
            }
            break;
            
        case 'cvv':
            if (value && !isValidCVV(value)) {
                isValid = false;
                errorMessage = 'CVV inválido';
            }
            break;
            
        case 'amount':
            const amount = parseFloat(value);
            if (value && (isNaN(amount) || amount <= 0 || amount > 10000)) {
                isValid = false;
                errorMessage = 'El monto debe ser mayor a 0 y menor a $10,000';
            }
            break;
    }
    
    if (!isValid) {
        showFieldError(field, errorMessage);
    } else {
        clearFieldError(field);
    }
    
    return isValid;
}

// Payment Processing
function initPaymentProcessing() {
    // Initialize payment validation rules
    window.paymentRules = {
        maxAmount: 10000,
        maxAttempts: 3,
        supportedCardTypes: ['visa', 'mastercard', 'amex', 'discover']
    };
}

// Handle Payment Submission
async function handlePaymentSubmission(event) {
    event.preventDefault();
    
    const form = event.target;
    const submitButton = document.getElementById('submit-payment');
    const submitText = document.getElementById('submit-text');
    const loadingSpinner = document.getElementById('loading-spinner');
    
    // Validate form
    if (!validatePaymentForm(form)) {
        PaySecure.showNotification('Por favor corrige los errores antes de continuar', 'error');
        return;
    }
    
    // Show loading state
    submitButton.disabled = true;
    submitText.textContent = 'Procesando...';
    loadingSpinner.classList.remove('hidden');
    
    // Collect form data
    const formData = new FormData(form);
    const paymentData = {
        full_name: formData.get('full_name'),
        rfc: formData.get('rfc'),
        card_number: formData.get('card_number').replace(/\s/g, ''),
        expiry_date: formData.get('expiry_date'),
        cvv: formData.get('cvv'),
        amount: parseFloat(formData.get('amount'))
    };
    
    try {
        // Process payment
        const response = await fetch('/api/process-payment', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(paymentData)
        });
        
        const result = await response.json();
        
        if (result.success) {
            // Show success modal
            showSuccessModal(result);
            
            // Reset form
            setTimeout(() => {
                form.reset();
                resetCardPreview();
            }, 2000);
        } else {
            // Show errors
            if (result.errors) {
                result.errors.forEach(error => {
                    PaySecure.showNotification(error, 'error');
                });
            }
        }
    } catch (error) {
        console.error('Payment error:', error);
        PaySecure.showNotification('Error al procesar el pago. Por favor intenta de nuevo.', 'error');
    } finally {
        // Reset button state
        submitButton.disabled = false;
        submitText.textContent = 'Procesar Pago Seguro';
        loadingSpinner.classList.add('hidden');
    }
}

// Validate Payment Form
function validatePaymentForm(form) {
    const inputs = form.querySelectorAll('input[required]');
    let isValid = true;
    
    inputs.forEach(input => {
        if (!validatePaymentField(input)) {
            isValid = false;
        }
    });
    
    return isValid;
}

// Show Success Modal
function showSuccessModal(data) {
    const modal = document.getElementById('success-modal');
    const message = document.getElementById('success-message');
    
    if (modal && message) {
        message.textContent = `Tu pago ha sido procesado exitosamente. Folio: ${data.invoice_number}`;
        modal.classList.remove('hidden');
        
        // Animate modal
        anime({
            targets: modal.querySelector('.bg-white'),
            scale: [0.8, 1],
            opacity: [0, 1],
            duration: 400,
            easing: 'easeOutElastic(1, .8)'
        });
    }
}

// Close Success Modal
function closeSuccessModal() {
    const modal = document.getElementById('success-modal');
    if (modal) {
        modal.classList.add('hidden');
    }
}

// Reset Card Preview
function resetCardPreview() {
    const previewNumber = document.getElementById('preview-number');
    const previewName = document.getElementById('preview-name');
    const previewExpiry = document.getElementById('preview-expiry');
    const previewLogo = document.getElementById('preview-logo');
    
    if (previewNumber) previewNumber.textContent = '**** **** **** ****';
    if (previewName) previewName.textContent = 'NOMBRE COMPLETO';
    if (previewExpiry) previewExpiry.textContent = 'MM/AA';
    if (previewLogo) previewLogo.innerHTML = '<i class="fas fa-credit-card text-white text-2xl"></i>';
    
    // Reset card color
    const cardPreview = document.getElementById('card-preview');
    if (cardPreview) {
        cardPreview.querySelector('.card-front').style.background = 
            'linear-gradient(135deg, #667eea 0%, #764ba2 100%)';
    }
}

// Animate Card Preview
function animateCardPreview() {
    const cardPreview = document.getElementById('card-preview');
    if (!cardPreview) return;
    
    // Initial animation
    anime({
        targets: cardPreview,
        scale: [0.9, 1],
        opacity: [0, 1],
        duration: 800,
        easing: 'easeOutElastic(1, .8)',
        delay: 500
    });
    
    // Hover effect
    cardPreview.addEventListener('mouseenter', function() {
        anime({
            targets: this,
            scale: 1.05,
            duration: 300,
            easing: 'easeOutExpo'
        });
    });
    
    cardPreview.addEventListener('mouseleave', function() {
        anime({
            targets: this,
            scale: 1,
            duration: 300,
            easing: 'easeOutExpo'
        });
    });
}

// Utility Functions
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

function showFieldError(field, message) {
    field.classList.add('error');
    
    const errorElement = document.getElementById(field.name + '-error') || 
                        document.getElementById(field.id + '-error');
    
    if (errorElement) {
        errorElement.textContent = message;
        errorElement.classList.add('show');
    }
    
    // Shake animation
    anime({
        targets: field,
        translateX: [-10, 10, -10, 10, 0],
        duration: 400,
        easing: 'easeInOutQuart'
    });
}

function clearFieldError(field) {
    field.classList.remove('error');
    
    const errorElement = document.getElementById(field.name + '-error') || 
                        document.getElementById(field.id + '-error');
    
    if (errorElement) {
        errorElement.classList.remove('show');
    }
}

// Validation Helpers
function isValidCardNumber(cardNumber) {
    if (!/^\d+$/.test(cardNumber)) return false;
    
    let sum = 0;
    let isEven = false;
    
    for (let i = cardNumber.length - 1; i >= 0; i--) {
        let digit = parseInt(cardNumber.charAt(i), 10);
        
        if (isEven) {
            digit *= 2;
            if (digit > 9) {
                digit -= 9;
            }
        }
        
        sum += digit;
        isEven = !isEven;
    }
    
    return sum % 10 === 0;
}

function isValidExpiryDate(date) {
    if (!/^\d{2}\/\d{2}$/.test(date)) return false;
    
    const [month, year] = date.split('/').map(Number);
    const now = new Date();
    const currentYear = now.getFullYear() % 100;
    const currentMonth = now.getMonth() + 1;
    
    if (year < currentYear || (year === currentYear && month < currentMonth)) {
        return false;
    }
    
    return month >= 1 && month <= 12;
}

function isValidCVV(cvv) {
    return /^\d{3,4}$/.test(cvv);
}

function isValidRFC(rfc) {
    const rfcRegex = /^[A-Z]{3,4}[0-9]{6}[A-Z0-9]{3}$/;
    return rfcRegex.test(rfc.toUpperCase());
}

// Export functions for global use
window.PaymentJS = {
    updateCardPreview,
    formatCardNumber,
    detectCardType,
    formatExpiryDate,
    validateCVV,
    formatAmount,
    updatePaymentSummary,
    closeSuccessModal
};