// Main JavaScript for PaySecure Application

document.addEventListener('DOMContentLoaded', function() {
    // Initialize mobile menu
    initMobileMenu();
    
    // Initialize tooltips
    initTooltips();
    
    // Initialize form validations
    initFormValidations();
    
    // Initialize animations
    initAnimations();
    
    // Initialize notifications
    initNotifications();
});

// Mobile Menu Toggle
function initMobileMenu() {
    const mobileMenuBtn = document.getElementById('mobile-menu-btn');
    const mobileMenu = document.getElementById('mobile-menu');
    
    if (mobileMenuBtn && mobileMenu) {
        mobileMenuBtn.addEventListener('click', function() {
            mobileMenu.classList.toggle('hidden');
            
            // Animate menu items
            if (!mobileMenu.classList.contains('hidden')) {
                const menuItems = mobileMenu.querySelectorAll('.mobile-nav-link');
                anime({
                    targets: menuItems,
                    translateX: [-50, 0],
                    opacity: [0, 1],
                    duration: 300,
                    delay: anime.stagger(50),
                    easing: 'easeOutExpo'
                });
            }
        });
        
        // Close menu when clicking outside
        document.addEventListener('click', function(event) {
            if (!mobileMenuBtn.contains(event.target) && !mobileMenu.contains(event.target)) {
                mobileMenu.classList.add('hidden');
            }
        });
    }
}

// Tooltip Initialization
function initTooltips() {
    const tooltipElements = document.querySelectorAll('[data-tooltip]');
    
    tooltipElements.forEach(element => {
        element.addEventListener('mouseenter', function() {
            const tooltip = this.querySelector('::before');
            if (tooltip) {
                anime({
                    targets: tooltip,
                    opacity: [0, 1],
                    translateY: [10, 0],
                    duration: 200,
                    easing: 'easeOutExpo'
                });
            }
        });
    });
}

// Form Validations
function initFormValidations() {
    const forms = document.querySelectorAll('form');
    
    forms.forEach(form => {
        const inputs = form.querySelectorAll('input, select, textarea');
        
        inputs.forEach(input => {
            // Real-time validation
            input.addEventListener('blur', function() {
                validateField(this);
            });
            
            input.addEventListener('input', function() {
                // Clear error on input
                clearFieldError(this);
            });
        });
        
        // Form submission
        form.addEventListener('submit', function(event) {
            if (!validateForm(this)) {
                event.preventDefault();
                showNotification('Por favor corrige los errores antes de continuar', 'error');
            }
        });
    });
}

// Field Validation
function validateField(field) {
    const value = field.value.trim();
    const fieldName = field.name || field.id;
    let isValid = true;
    let errorMessage = '';
    
    // Required field validation
    if (field.hasAttribute('required') && !value) {
        isValid = false;
        errorMessage = 'Este campo es requerido';
    }
    
    // Specific field validations
    switch (fieldName) {
        case 'email':
            if (value && !isValidEmail(value)) {
                isValid = false;
                errorMessage = 'Por favor ingresa un email válido';
            }
            break;
            
        case 'username':
            if (value && value.length < 3) {
                isValid = false;
                errorMessage = 'El usuario debe tener al menos 3 caracteres';
            }
            break;
            
        case 'password':
            if (value && value.length < 6) {
                isValid = false;
                errorMessage = 'La contraseña debe tener al menos 6 caracteres';
            }
            break;
            
        case 'card_number':
            if (value && !isValidCardNumber(value.replace(/\s/g, ''))) {
                isValid = false;
                errorMessage = 'Número de tarjeta inválido';
            }
            break;
            
        case 'expiry_date':
            if (value && !isValidExpiryDate(value)) {
                isValid = false;
                errorMessage = 'Fecha de expiración inválida';
            }
            break;
            
        case 'cvv':
            if (value && !isValidCVV(value)) {
                isValid = false;
                errorMessage = 'CVV inválido';
            }
            break;
            
        case 'amount':
            if (value && (parseFloat(value) <= 0 || parseFloat(value) > 10000)) {
                isValid = false;
                errorMessage = 'El monto debe ser mayor a 0 y menor a $10,000';
            }
            break;
            
        case 'rfc':
            if (value && !isValidRFC(value)) {
                isValid = false;
                errorMessage = 'RFC inválido';
            }
            break;
    }
    
    // Show/hide error
    if (!isValid) {
        showFieldError(field, errorMessage);
    } else {
        clearFieldError(field);
    }
    
    return isValid;
}

// Form Validation
function validateForm(form) {
    const inputs = form.querySelectorAll('input, select, textarea');
    let isValid = true;
    
    inputs.forEach(input => {
        if (!validateField(input)) {
            isValid = false;
        }
    });
    
    return isValid;
}

// Show Field Error
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

// Clear Field Error
function clearFieldError(field) {
    field.classList.remove('error');
    
    const errorElement = document.getElementById(field.name + '-error') || 
                        document.getElementById(field.id + '-error');
    
    if (errorElement) {
        errorElement.classList.remove('show');
    }
}

// Validation Helpers
function isValidEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
}

function isValidCardNumber(cardNumber) {
    // Luhn algorithm
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

// Animation Initialization
function initAnimations() {
    // Animate elements on scroll
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('animate-in');
                
                // Specific animations based on element type
                if (entry.target.classList.contains('stat-card')) {
                    animateStatCard(entry.target);
                } else if (entry.target.classList.contains('action-card')) {
                    animateActionCard(entry.target);
                }
            }
        });
    }, observerOptions);
    
    // Observe elements
    const animateElements = document.querySelectorAll('.stat-card, .action-card, .transaction-row');
    animateElements.forEach(el => observer.observe(el));
}

// Animate Stat Card
function animateStatCard(element) {
    const numberElement = element.querySelector('.text-3xl');
    if (numberElement) {
        const finalValue = parseInt(numberElement.textContent) || 0;
        
        anime({
            targets: { value: 0 },
            value: finalValue,
            duration: 2000,
            easing: 'easeOutExpo',
            update: function(anim) {
                numberElement.textContent = Math.floor(anim.animatables[0].target.value);
            }
        });
    }
}

// Animate Action Card
function animateActionCard(element) {
    anime({
        targets: element,
        scale: [0.9, 1],
        opacity: [0, 1],
        duration: 600,
        easing: 'easeOutElastic(1, .8)'
    });
}

// Notification System
function initNotifications() {
    // Auto-dismiss notifications after 5 seconds
    const notifications = document.querySelectorAll('.alert');
    notifications.forEach((notification, index) => {
        setTimeout(() => {
            if (notification.parentNode) {
                anime({
                    targets: notification,
                    opacity: [1, 0],
                    translateX: [0, 100],
                    duration: 300,
                    easing: 'easeInExpo',
                    complete: () => {
                        if (notification.parentNode) {
                            notification.parentNode.removeChild(notification);
                        }
                    }
                });
            }
        }, 5000 + (index * 200));
    });
}

// Show Notification
function showNotification(message, type = 'info', duration = 5000) {
    const notification = document.createElement('div');
    notification.className = `alert alert-${type}`;
    notification.innerHTML = `
        <i class="fas ${getNotificationIcon(type)} mr-2"></i>
        ${message}
        <button class="ml-4 text-gray-400 hover:text-gray-600" onclick="this.parentElement.remove()">
            <i class="fas fa-times"></i>
        </button>
    `;
    
    const container = document.querySelector('.fixed.top-20.right-4');
    if (container) {
        container.appendChild(notification);
        
        // Auto-dismiss
        setTimeout(() => {
            if (notification.parentNode) {
                anime({
                    targets: notification,
                    opacity: [1, 0],
                    translateX: [0, 100],
                    duration: 300,
                    easing: 'easeInExpo',
                    complete: () => {
                        if (notification.parentNode) {
                            notification.parentNode.removeChild(notification);
                        }
                    }
                });
            }
        }, duration);
    }
}

// Get Notification Icon
function getNotificationIcon(type) {
    switch (type) {
        case 'success': return 'fa-check-circle';
        case 'error': return 'fa-times-circle';
        case 'warning': return 'fa-exclamation-triangle';
        default: return 'fa-info-circle';
    }
}

// Utility Functions
function formatCurrency(amount) {
    return new Intl.NumberFormat('es-MX', {
        style: 'currency',
        currency: 'MXN'
    }).format(amount);
}

function formatDate(date) {
    return new Intl.DateTimeFormat('es-MX', {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    }).format(new Date(date));
}

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

// API Helper
async function apiRequest(endpoint, method = 'GET', data = null) {
    const options = {
        method,
        headers: {
            'Content-Type': 'application/json',
        },
    };
    
    if (data) {
        options.body = JSON.stringify(data);
    }
    
    try {
        const response = await fetch(endpoint, options);
        const result = await response.json();
        
        if (!response.ok) {
            throw new Error(result.message || 'Error en la solicitud');
        }
        
        return result;
    } catch (error) {
        console.error('API Error:', error);
        showNotification(error.message, 'error');
        throw error;
    }
}

// Copy to Clipboard
function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(() => {
        showNotification('Texto copiado al portapapeles', 'success', 2000);
    }).catch(() => {
        showNotification('Error al copiar texto', 'error');
    });
}

// Export functions for global use
window.PaySecure = {
    showNotification,
    formatCurrency,
    formatDate,
    apiRequest,
    copyToClipboard,
    validateField,
    validateForm
};