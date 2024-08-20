document.addEventListener('DOMContentLoaded', function() {
    var dropdown = document.querySelector('.dropdown');
    dropdown.addEventListener('click', function() {
        this.classList.toggle('active');
        var dropdownContent = this.querySelector('.dropdown-content');
        dropdownContent.classList.toggle('show');
    });

    window.addEventListener('click', function(event) {
        if (!event.target.matches('.dropbtn')) {
            var dropdowns = document.querySelectorAll('.dropdown-content');
            dropdowns.forEach(function(dropdown) {
                if (dropdown.classList.contains('show')) {
                    dropdown.classList.remove('show');
                    dropdown.parentElement.classList.remove('active');
                }
            });
        }
    });
});

function logout() {
    localStorage.removeItem('token');
    window.location.href = logoutUrl;
}

function setTheme(theme) {
    const body = document.body;
    body.className = ''; // Remove all classes from the body
    body.classList.add(theme); // Add the selected theme
    localStorage.setItem('theme', theme); // Optionally store the theme in localStorage to persist across reloads
}

function toggleTheme() {
    const body = document.body;
    if (body.classList.contains('light-theme')) {
        setTheme('dark-theme');
    } else {
        setTheme('light-theme');
    }
}

function initializeTheme() {
    const storedTheme = localStorage.getItem('theme');
    if (storedTheme === 'dark-theme') {
        setTheme('dark-theme');
        themeToggle.checked = true;
    } else {
        setTheme('light-theme');
        themeToggle.checked = false;
    }
}

window.addEventListener('load', initializeTheme);
document.getElementById('themeToggle').addEventListener('change', toggleTheme);

function closeMessagesModal() {
    // $('#messages-container').empty();
    $('#messages-modal').modal('hide');
    $('.modal-backdrop').remove();
}

$(document).ready(function() {
    console.log("Document ready");

    $('#notification-icon').click(function() {
        console.log("Notification icon clicked");
        toggleMessagesModal();
        $('#messages-modal .modal-header').show();
    });

    function toggleMessagesModal() {
        if ($('#messages-modal').hasClass('show')) {
            closeMessagesModal();
        } else {
            $('#messages-modal').modal('show');
        }
    }

    $('#messages-modal').on('hidden.bs.modal', function() {
        $('#messages-modal .modal-header').hide();
    });

    $('#close-button').click(function() {
        $('#messages-modal').modal('hide');
    });

    $('#messages-modal').on('hidden.bs.modal', function() {
        $('.modal-backdrop').remove();
    });

    $(document).on('click', function(event) {
        if (!$('#messages-modal').hasClass('show')) {
            return;
        }
        if (!$(event.target).closest('.modal').length && !$(event.target).is('#notification-icon')) {
            closeMessagesModal();
        }
    });
});