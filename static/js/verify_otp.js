//  // Get the remaining time in seconds from Flask template
//  var remainingTimeSeconds = { remaining_time_seconds };
//  console.log('this is console log remaining time: ',remainingTimeSeconds);

//  function formatSeconds(seconds) {
//      return seconds < 10 ? "0" + seconds : seconds;
//  }

//  // Function to update the countdown timer
//  function updateCountdown() {
//      var minutes = Math.floor(remainingTimeSeconds / 60);
//      var seconds = remainingTimeSeconds % 60;
     
//      var formattedSeconds = formatSeconds(seconds);

//      document.getElementById("countdown").innerHTML = "Remaining time: " + minutes + "m " + seconds + "s";

//      // If the countdown is over, display expired message
//      if (remainingTimeSeconds <= 0) {
//          clearInterval(countdownInterval);
//          document.getElementById("countdown").innerHTML = "OTP expired. <a href='/resend_otp'>Resend OTP</a>";
//      }

//      remainingTimeSeconds--; // Decrement remaining time by 1 second
//  }

//  // Update countdown every second
//  var countdownInterval = setInterval(updateCountdown, 1000);
//  updateCountdown(); // Call the function immediately to start the countdown

// document.addEventListener('DOMContentLoaded', function() {
//     var countdownElement = document.getElementById('countdown');
//     var remainingTimeSeconds = parseInt(countdownElement.getAttribute('data-remaining-time'), 10);
    
//     function formatSeconds(seconds) {
//         return seconds < 10 ? "0" + seconds : seconds;
//     }

//     function updateCountdown() {
//         var minutes = Math.floor(remainingTimeSeconds / 60);
//         var seconds = remainingTimeSeconds % 60;

//         var formattedSeconds = formatSeconds(seconds);

//         countdownElement.innerHTML = "Remaining time: " + minutes + "m " + formattedSeconds + "s";

//         if (remainingTimeSeconds <= 0) {
//             clearInterval(countdownInterval);
//             countdownElement.innerHTML = "OTP expired. <a href='/resend_otp'>Resend OTP</a>";
//         }

//         remainingTimeSeconds--;
//     }

//     var countdownInterval = setInterval(updateCountdown, 1000);
//     updateCountdown();
// });

document.addEventListener('DOMContentLoaded', function() {
    const inputs = document.querySelectorAll(".otp-field > input");
    const button = document.querySelector(".btn");
    const countdownElement = document.getElementById('countdown');
    let remainingTimeSeconds = parseInt(countdownElement.getAttribute('data-remaining-time'), 10);

    // OTP input handling
    window.addEventListener("load", () => inputs[0].focus());
    button.setAttribute("disabled", "disabled");

    inputs[0].addEventListener("paste", function (event) {
        event.preventDefault();

        const pastedValue = (event.clipboardData || window.clipboardData).getData("text");
        const otpLength = inputs.length;

        for (let i = 0; i < otpLength; i++) {
            if (i < pastedValue.length) {
                inputs[i].value = pastedValue[i];
                inputs[i].removeAttribute("disabled");
                inputs[i].focus();
            } else {
                inputs[i].value = "";
                inputs[i].focus();
            }
        }
    });

    inputs.forEach((input, index1) => {
        input.addEventListener("keyup", (e) => {
            const currentInput = input;
            const nextInput = input.nextElementSibling;
            const prevInput = input.previousElementSibling;

            if (currentInput.value.length > 1) {
                currentInput.value = "";
                return;
            }

            if (nextInput && nextInput.hasAttribute("disabled") && currentInput.value !== "") {
                nextInput.removeAttribute("disabled");
                nextInput.focus();
            }

            if (e.key === "Backspace") {
                inputs.forEach((input, index2) => {
                    if (index1 <= index2 && prevInput) {
                        input.setAttribute("disabled", true);
                        input.value = "";
                        prevInput.focus();
                    }
                });
            }

            button.classList.remove("active");
            button.setAttribute("disabled", "disabled");

            const inputsNo = inputs.length;
            if (!inputs[inputsNo - 1].disabled && inputs[inputsNo - 1].value !== "") {
                button.classList.add("active");
                button.removeAttribute("disabled");
                return;
            }
        });
    });

    // Countdown timer handling
    function formatSeconds(seconds) {
        return seconds < 10 ? "0" + seconds : seconds;
    }

    function updateCountdown() {
        const minutes = Math.floor(remainingTimeSeconds / 60);
        const seconds = remainingTimeSeconds % 60;

        countdownElement.innerHTML = "Remaining time: " + minutes + "m " + formatSeconds(seconds) + "s";

        if (remainingTimeSeconds <= 0) {
            clearInterval(countdownInterval);
            countdownElement.innerHTML = "OTP expired. <a href='/resend_otp'>Resend OTP</a>";
        }

        remainingTimeSeconds--;
    }

    const countdownInterval = setInterval(updateCountdown, 1000);
    updateCountdown();
});
