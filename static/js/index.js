function login() {
    // Clear token from Local Storage
    localStorage.removeItem('token');

    // Redirect to logout page or perform any other action after logout
    window.location.href = "{{ url_for('user.login_user') }}";
    }
    document.getElementById('login-email').value = '';
    document.getElementById('login-password').value = '';

    document.addEventListener('DOMContentLoaded', function() {
    const passwordField = document.getElementById('login-password');
    const togglePassword = document.getElementById('togglePassword');

        togglePassword.addEventListener('click', function() {
            const type = passwordField.getAttribute('type') === 'password' ? 'text' : 'password';
            passwordField.setAttribute('type', type);
            // Change eye icon based on password visibility
            togglePassword.textContent = type === 'password' ? '🙈' : ' 🐵 ';
            });
    });