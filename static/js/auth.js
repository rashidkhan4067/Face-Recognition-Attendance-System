// Authentication Pages JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // Initialize form enhancements
    initializeFormEnhancements();
    initializeAlerts();
    initializeFormValidation();
    initializeLoadingStates();
});

function initializeFormEnhancements() {
    // Add interactive effects to form inputs
    const inputs = document.querySelectorAll('.form-floating input, .form-floating select');
    
    inputs.forEach(input => {
        // Focus effects
        input.addEventListener('focus', function() {
            this.parentElement.style.transform = 'scale(1.02)';
            this.parentElement.style.transition = 'transform 0.3s ease';
        });
        
        input.addEventListener('blur', function() {
            this.parentElement.style.transform = 'scale(1)';
        });

        // Real-time validation feedback
        input.addEventListener('input', function() {
            validateField(this);
        });

        // Handle floating labels for select elements
        if (input.tagName === 'SELECT') {
            input.addEventListener('change', function() {
                const label = this.parentElement.querySelector('label');
                if (this.value) {
                    label.classList.add('active');
                } else {
                    label.classList.remove('active');
                }
            });
        }
    });
}

function initializeAlerts() {
    // Auto-hide alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            if (alert && alert.parentNode) {
                const bsAlert = new bootstrap.Alert(alert);
                bsAlert.close();
            }
        }, 5000);
    });
}

function initializeFormValidation() {
    const forms = document.querySelectorAll('form');
    
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            if (!validateForm(this)) {
                e.preventDefault();
                e.stopPropagation();
            } else {
                // Add loading state to submit button
                const submitBtn = this.querySelector('button[type="submit"]');
                if (submitBtn) {
                    submitBtn.classList.add('loading');
                    submitBtn.disabled = true;
                }
            }
        });
    });
}

function initializeLoadingStates() {
    // Handle form submission loading states
    const forms = document.querySelectorAll('form');
    
    forms.forEach(form => {
        form.addEventListener('submit', function() {
            const submitBtn = this.querySelector('.btn-auth');
            if (submitBtn) {
                submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Please wait...';
                submitBtn.disabled = true;
            }
        });
    });
}

function validateField(field) {
    const value = field.value.trim();
    const fieldType = field.type;
    const fieldName = field.name;
    let isValid = true;
    let errorMessage = '';

    // Remove existing error messages
    removeFieldError(field);

    // Required field validation
    if (field.hasAttribute('required') && !value) {
        isValid = false;
        errorMessage = 'This field is required.';
    }

    // Email validation
    if (fieldType === 'email' && value) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailRegex.test(value)) {
            isValid = false;
            errorMessage = 'Please enter a valid email address.';
        }
    }

    // Password validation
    if (fieldName === 'password1' && value) {
        if (value.length < 8) {
            isValid = false;
            errorMessage = 'Password must be at least 8 characters long.';
        }
    }

    // Password confirmation validation
    if (fieldName === 'password2' && value) {
        const password1 = document.querySelector('input[name="password1"]');
        if (password1 && value !== password1.value) {
            isValid = false;
            errorMessage = 'Passwords do not match.';
        }
    }

    // Employee ID validation
    if (fieldName === 'employee_id' && value) {
        const empIdRegex = /^[A-Z0-9]+$/;
        if (!empIdRegex.test(value)) {
            isValid = false;
            errorMessage = 'Employee ID must contain only uppercase letters and numbers.';
        }
    }

    // Phone number validation
    if (fieldName === 'phone_number' && value) {
        const phoneRegex = /^\+?1?\d{9,15}$/;
        if (!phoneRegex.test(value.replace(/\s/g, ''))) {
            isValid = false;
            errorMessage = 'Please enter a valid phone number.';
        }
    }

    // Update field appearance
    if (isValid) {
        field.classList.remove('is-invalid');
        field.classList.add('is-valid');
    } else {
        field.classList.remove('is-valid');
        field.classList.add('is-invalid');
        showFieldError(field, errorMessage);
    }

    return isValid;
}

function validateForm(form) {
    const inputs = form.querySelectorAll('input[required], select[required]');
    let isFormValid = true;

    inputs.forEach(input => {
        if (!validateField(input)) {
            isFormValid = false;
        }
    });

    return isFormValid;
}

function showFieldError(field, message) {
    const errorDiv = document.createElement('div');
    errorDiv.className = 'text-danger field-error';
    errorDiv.textContent = message;
    
    const parent = field.parentElement;
    parent.appendChild(errorDiv);
}

function removeFieldError(field) {
    const parent = field.parentElement;
    const existingError = parent.querySelector('.field-error');
    if (existingError) {
        existingError.remove();
    }
}

// Utility functions
function showNotification(message, type = 'info') {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    const container = document.querySelector('.login-container, .register-container');
    if (container) {
        container.insertBefore(alertDiv, container.firstChild);
        
        // Auto-hide after 5 seconds
        setTimeout(() => {
            if (alertDiv && alertDiv.parentNode) {
                const bsAlert = new bootstrap.Alert(alertDiv);
                bsAlert.close();
            }
        }, 5000);
    }
}

// Password strength indicator
function initializePasswordStrength() {
    const passwordField = document.querySelector('input[name="password1"]');
    if (passwordField) {
        passwordField.addEventListener('input', function() {
            const strength = calculatePasswordStrength(this.value);
            updatePasswordStrengthIndicator(strength);
        });
    }
}

function calculatePasswordStrength(password) {
    let strength = 0;
    
    if (password.length >= 8) strength += 1;
    if (password.match(/[a-z]/)) strength += 1;
    if (password.match(/[A-Z]/)) strength += 1;
    if (password.match(/[0-9]/)) strength += 1;
    if (password.match(/[^a-zA-Z0-9]/)) strength += 1;
    
    return strength;
}

function updatePasswordStrengthIndicator(strength) {
    // This can be implemented to show password strength
    // For now, we'll just add classes to the password field
    const passwordField = document.querySelector('input[name="password1"]');
    if (passwordField) {
        passwordField.classList.remove('weak', 'medium', 'strong');
        
        if (strength < 3) {
            passwordField.classList.add('weak');
        } else if (strength < 5) {
            passwordField.classList.add('medium');
        } else {
            passwordField.classList.add('strong');
        }
    }
}

// Initialize password strength on page load
document.addEventListener('DOMContentLoaded', function() {
    initializePasswordStrength();
});

// Handle form reset
function resetForm(formId) {
    const form = document.getElementById(formId);
    if (form) {
        form.reset();
        
        // Remove validation classes
        const inputs = form.querySelectorAll('input, select');
        inputs.forEach(input => {
            input.classList.remove('is-valid', 'is-invalid');
            removeFieldError(input);
        });
        
        // Reset submit button
        const submitBtn = form.querySelector('.btn-auth');
        if (submitBtn) {
            submitBtn.disabled = false;
            submitBtn.classList.remove('loading');
        }
    }
}

// Keyboard navigation enhancements
document.addEventListener('keydown', function(e) {
    // Enter key on form fields
    if (e.key === 'Enter' && e.target.tagName === 'INPUT') {
        const form = e.target.closest('form');
        if (form) {
            const inputs = Array.from(form.querySelectorAll('input, select'));
            const currentIndex = inputs.indexOf(e.target);
            
            if (currentIndex < inputs.length - 1) {
                e.preventDefault();
                inputs[currentIndex + 1].focus();
            }
        }
    }
});
