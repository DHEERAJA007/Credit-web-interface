// DOM Elements
const form = document.getElementById('predictionForm');
const submitBtn = document.getElementById('submitBtn');
const btnLoader = document.getElementById('btnLoader');
const progressFill = document.getElementById('progressFill');
const progressText = document.getElementById('progressText');
const resultsContainer = document.getElementById('results');
const resultIcon = document.getElementById('resultIcon');
const resultTitle = document.getElementById('resultTitle');
const resultStatus = document.getElementById('resultStatus');
const statusText = document.getElementById('statusText');
const resultMessage = document.getElementById('resultMessage');

// Progress tracking
let totalFields = 0;
let filledFields = 0;

document.addEventListener('DOMContentLoaded', function () {
    initializeForm();
    setupEventListeners();
});

function initializeForm() {
    const requiredFields = form.querySelectorAll('input[required], select[required], textarea[required]');
    totalFields = requiredFields.length;
    updateProgress();

    document.querySelectorAll('.form-section').forEach((section, index) => {
        setTimeout(() => section.classList.add('fade-in'), index * 100);
    });
    
}

function setupEventListeners() {

    const inputs = form.querySelectorAll('input, select, textarea');
    inputs.forEach(input => {
        input.addEventListener('input', updateProgress);
        input.addEventListener('change', updateProgress);
        input.addEventListener('blur', validateField);
        input.addEventListener('input', clearFieldError);
    });
}

function updateProgress() {
    const requiredFields = form.querySelectorAll('input[required], select[required], textarea[required]');
    filledFields = Array.from(requiredFields).filter(field => field.value.trim() !== '').length;

    const percentage = (filledFields / totalFields) * 100;
    progressFill.style.width = percentage + '%';

    if (percentage === 0) {
        progressText.textContent = 'Fill out the form to get started';
    } else if (percentage < 100) {
        progressText.textContent = `Progress: ${Math.round(percentage)}% complete (${filledFields}/${totalFields} fields)`;
    } else {
        progressText.textContent = 'Form complete! Ready for analysis.';
    }
}

function validateField(event) {
    const field = event.target;
    const value = field.value.trim();

    field.classList.remove('error');

    if (field.hasAttribute('required') && !value) {
        showFieldError(field, 'This field is required');
        return false;
    }

    if (field.type === 'number' && value && isNaN(value)) {
        showFieldError(field, 'Please enter a valid number');
        return false;
    }

    if (field.type === 'email' && value && !isValidEmail(value)) {
        showFieldError(field, 'Please enter a valid email address');
        return false;
    }

    return true;
}

function showFieldError(field, message) {
    field.classList.add('error');

    const existingError = field.parentNode.querySelector('.error-message');
    if (existingError) existingError.remove();

    const errorDiv = document.createElement('div');
    errorDiv.className = 'error-message';
    errorDiv.textContent = message;
    errorDiv.style.color = '#e53e3e';
    errorDiv.style.fontSize = '0.75rem';
    errorDiv.style.marginTop = '0.25rem';

    field.parentNode.appendChild(errorDiv);
}

function clearFieldError(event) {
    const field = event.target;
    field.classList.remove('error');

    const errorMessage = field.parentNode.querySelector('.error-message');
    if (errorMessage) errorMessage.remove();
}

async function handleSubmit(event) {
    event.preventDefault();

    let isValid = true;
    const inputs = form.querySelectorAll('input, select, textarea');

    inputs.forEach(input => {
        if (!validateField({ target: input })) isValid = false;
    });

    if (!isValid) {
        showNotification('Please correct the errors in the form', 'error');
        const firstError = form.querySelector('.error');
        if (firstError) firstError.scrollIntoView({ behavior: 'smooth', block: 'center' });
        return;
    }

    setLoadingState(true);

    try {
        const formData = new FormData(form);

        const response = await fetch("/debug", {
            method: "POST",
            body: formData  // ✅ Don't manually set Content-Type for FormData
        });

        if (!response.ok) {
            const errMessage = await response.text();
            throw new Error(`Server error (${response.status}): ${errMessage}`);
        }

        // ✅ Expect HTML response (not JSON)
        const resultHtml = await response.text();

        // Display it in a container or replace the body (for testing)
        const debugContainer = document.getElementById('results');
        debugContainer.innerHTML = resultHtml;
        debugContainer.classList.remove('hidden');
        debugContainer.classList.add('slide-up');
        debugContainer.scrollIntoView({ behavior: 'smooth', block: 'center' });

    } catch (error) {
        console.error('Error:', error);
        showNotification('Connection error. Please check if the server is running.', 'error');
    } finally {
        setLoadingState(false);
    }
}


function setLoadingState(loading) {
    if (loading) {
        submitBtn.classList.add('loading');
        submitBtn.disabled = true;
        btnLoader.style.display = 'inline-block';
    } else {
        submitBtn.classList.remove('loading');
        submitBtn.disabled = false;
        btnLoader.style.display = 'none';
    }
}

function displayResults(result) {
    resultsContainer.classList.remove('hidden');
    resultsContainer.classList.add('slide-up');
    resultsContainer.scrollIntoView({ behavior: 'smooth', block: 'center' });

    if (result.error) {
        resultIcon.className = 'result-icon danger';
        resultIcon.innerHTML = '<i class="fas fa-times-circle"></i>';
        resultTitle.textContent = 'Analysis Error';
        statusText.textContent = 'Error';
        statusText.className = 'status-text danger';
        resultMessage.textContent = result.error;
    } else {
        const predictionText = String(result.prediction).toLowerCase();
        const isPositive = predictionText === "1" || predictionText === "creditworthy" || predictionText === "yes";

        if (isPositive) {
            resultIcon.className = 'result-icon success';
            resultIcon.innerHTML = '<i class="fas fa-check-circle"></i>';
            statusText.textContent = 'Creditworthy';
            statusText.className = 'status-text success';
            resultMessage.textContent = 'Congratulations! Based on the provided information, you appear to be creditworthy for the requested loan.';
        } else {
            resultIcon.className = 'result-icon danger';
            resultIcon.innerHTML = '<i class="fas fa-times-circle"></i>';
            statusText.textContent = 'Not Creditworthy';
            statusText.className = 'status-text danger';
            resultMessage.textContent = 'Based on the current financial information, the assessment indicates potential credit risk. Consider improving your credit profile and financial standing before reapplying.';
        }

        if (result.probability !== undefined) {
            resultMessage.textContent += `\nConfidence: ${(result.probability * 100).toFixed(2)}%`;
        }

        resultTitle.textContent = 'Credit Assessment Complete';
    }
}

function resetForm() {
    form.reset();
    resultsContainer.classList.add('hidden');
    resultsContainer.classList.remove('slide-up');
    filledFields = 0;
    updateProgress();

    const errorMessages = form.querySelectorAll('.error-message');
    errorMessages.forEach(msg => msg.remove());

    const errorFields = form.querySelectorAll('.error');
    errorFields.forEach(field => field.classList.remove('error'));

    window.scrollTo({ top: 0, behavior: 'smooth' });
    showNotification('Form reset successfully', 'success');
}

function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.innerHTML = `
        <div class="notification-content">
            <i class="fas fa-${type === 'error' ? 'exclamation-triangle' : type === 'success' ? 'check-circle' : 'info-circle'}"></i>
            <span>${message}</span>
        </div>
    `;

    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: ${type === 'error' ? '#fed7d7' : type === 'success' ? '#c6f6d5' : '#bee3f8'};
        color: ${type === 'error' ? '#c53030' : type === 'success' ? '#2f855a' : '#2b6cb0'};
        padding: 1rem 1.5rem;
        border-radius: 12px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        z-index: 10000;
        animation: slideIn 0.3s ease-out;
        max-width: 400px;
        border: 1px solid ${type === 'error' ? '#feb2b2' : type === 'success' ? '#9ae6b4' : '#90cdf4'};
    `;

    notification.querySelector('.notification-content').style.cssText = `
        display: flex;
        align-items: center;
        gap: 0.5rem;
        font-weight: 500;
    `;

    document.body.appendChild(notification);

    setTimeout(() => {
        notification.style.animation = 'slideOut 0.3s ease-in forwards';
        setTimeout(() => {
            if (notification.parentNode) notification.parentNode.removeChild(notification);
        }, 300);
    }, 5000);
}

function isValidEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
}

const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from { transform: translateX(100%); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
    }
    @keyframes slideOut {
        from { transform: translateX(0); opacity: 1; }
        to { transform: translateX(100%); opacity: 0; }
    }
    .error {
        border-color: #e53e3e !important;
        box-shadow: 0 0 0 3px rgba(229, 62, 62, 0.1) !important;
    }
`;
document.head.appendChild(style);

window.resetForm = resetForm;
