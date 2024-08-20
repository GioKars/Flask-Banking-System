document.querySelector('.change-password').addEventListener('click', function() {
    var passwordSection = document.getElementById('password-section');
    var newPasswordInput = document.createElement('input');
    newPasswordInput.type = 'password';
    newPasswordInput.name = 'new_password';
    newPasswordInput.placeholder = 'New Password';
    newPasswordInput.autocomplete = 'off'
    var oldPasswordInput = document.createElement('input');
    oldPasswordInput.type = 'password';
    oldPasswordInput.name = 'old_password';
    oldPasswordInput.placeholder = 'Old Password';
    oldPasswordInput.autocomplete = 'off'
    passwordSection.appendChild(oldPasswordInput);
    passwordSection.appendChild(newPasswordInput);
    passwordSection.removeChild(this);
});

document.getElementById('settings-form').addEventListener('submit', function(event) {
    event.preventDefault(); // Prevent form submission

    var oldPassword = document.querySelector('input[name="old_password"]').value;
    var newPassword = document.querySelector('input[name="new_password"]').value;

    // Send an AJAX request to the server to validate the old password and change it
    var xhr = new XMLHttpRequest();
    xhr.open('POST', '/change_password', true);
    xhr.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
    xhr.onreadystatechange = function() {
        if (xhr.readyState === XMLHttpRequest.DONE) {
            if (xhr.status === 200) {
                // Password change successful
                alert('Password changed successfully!');
            } else {
                // Password change failed, display error message
                alert('Failed to change password: ' + xhr.responseText);
            }
        }
    };
    xhr.send('old_password=' + encodeURIComponent(oldPassword) + '&new_password=' + encodeURIComponent(newPassword));
});

