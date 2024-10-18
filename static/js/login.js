document.addEventListener('DOMContentLoaded', function() {
    const loginForm = document.getElementById('loginForm');
    const errorMessage = document.getElementById('error-message');
    const forgotPasswordLink = document.getElementById('forgotPassword');

    loginForm.addEventListener('submit', function(e) {
        e.preventDefault();
        if (validateForm()) {
            this.submit();
        }
    });

    forgotPasswordLink.addEventListener('click', function(e) {
        e.preventDefault();
        const email = document.getElementById('email').value;
        if (validateEmail(email)) {
            resetPassword(email);
        } else {
            displayError('Please enter a valid email address.');
        }
    });

    function validateForm() {
        const email = document.getElementById('email').value;
        const password = document.getElementById('password').value;
        
        if (!validateEmail(email)) {
            displayError('Please enter a valid email address.');
            return false;
        }
        
        if (password.length < 8) {
            displayError('Password must be at least 8 characters long.');
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

    function resetPassword(email) {
        fetch('/reset-password', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ email: email }),
        })
        .then(response => response.json())
        .then(data => {
            if (data.message) {
                alert(data.message);
            } else {
                displayError(data.error);
            }
        })
        .catch(error => {
            console.error('Error:', error);
            displayError('An error occurred. Please try again.');
        });
    }

    function signInWithGoogle() {
        // Implement Google Sign-In logic here
        console.log('Google Sign-In clicked');
    }

    window.signInWithGoogle = signInWithGoogle;
});
