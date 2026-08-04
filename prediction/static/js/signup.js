document.addEventListener("DOMContentLoaded", function () {

    const form = document.querySelector(".signup-form");

    form.addEventListener("submit", function (e) {

        const fullname = document.querySelector("input[name='fullname']").value.trim();
        const username = document.querySelector("input[name='username']").value.trim();
        const email = document.querySelector("input[name='email']").value.trim();
        const phone = document.querySelector("input[name='phone']").value.trim();
        const age = document.querySelector("input[name='age']").value.trim();
        const gender = document.querySelector("select[name='gender']").value;
        const password = document.getElementById("password").value;
        const confirmPassword = document.getElementById("confirm_password").value;

        // Full Name
        if (fullname === "") {
            alert("Please enter your Full Name.");
            e.preventDefault();
            return;
        }

        // Username
        if (username.length < 3) {
            alert("Username must contain at least 3 characters.");
            e.preventDefault();
            return;
        }

        // Email Validation
        const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

        if (!emailPattern.test(email)) {
            alert("Please enter a valid Email Address.");
            e.preventDefault();
            return;
        }

        // Phone Validation
        const phonePattern = /^[0-9]{10}$/;

        if (!phonePattern.test(phone)) {
            alert("Phone Number must contain exactly 10 digits.");
            e.preventDefault();
            return;
        }

        // Age Validation
        if (parseInt(age) <= 15) {
            alert("Age must be greater than 15.");
            e.preventDefault();
            return;
        }

        // Gender Validation
        if (gender === "") {
            alert("Please select your Gender.");
            e.preventDefault();
            return;
        }

        // Strong Password Validation
        const strongPassword =
            /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&]).{8,}$/;

        if (!strongPassword.test(password)) {
            alert(
                "Password must contain:\n\n" +
                "• 1 Uppercase Letter\n" +
                "• 1 Lowercase Letter\n" +
                "• 1 Number\n" +
                "• 1 Special Character\n" +
                "• Minimum 8 Characters"
            );
            e.preventDefault();
            return;
        }

        // Confirm Password
        if (password !== confirmPassword) {
            alert("Password and Confirm Password do not match.");
            e.preventDefault();
            return;
        }

        // Success
        alert("Form validated successfully!");

        // ✅ DO NOT use window.location.href here.
        // Let the form submit naturally to Django.
    });

});