document.addEventListener('DOMContentLoaded', function() {
    const registerForm = document.getElementById('registerForm');
    const errorMessage = document.getElementById('error-message');

    registerForm.addEventListener('submit', function(e) {
        e.preventDefault();
        if (validateForm()) {
            this.submit();
        }
    });

    function validateForm() {
        const email = document.getElementById('email').value;
        const password = document.getElementById('password').value;
        const confirmPassword = document.getElementById('confirmPassword').value;
        
        if (!validateEmail(email)) {
            displayError('Please enter a valid email address.');
            return false;
        }
        
        if (password.length < 8) {
            displayError('Password must be at least 8 characters long.');
            return false;
        }
        
        if (password !== confirmPassword) {
            displayError('Passwords do not match.');
            return false;
        }
        
        return true;
    }

    function validateEmail(email) {
        const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return re.test(email);
    }

    function displayError(message) {
        errorMessage.textContent = message;
        errorMessage.style.display = 'block';
    }

    function signUpWithGoogle() {
        // Implement Google Sign-Up logic here
        console.log('Google Sign-Up clicked');
    }

    window.signUpWithGoogle = signUpWithGoogle;
});
