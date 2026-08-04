document.addEventListener("DOMContentLoaded", function () {

    const form = document.querySelector("form");

    form.addEventListener("submit", function (event) {

        const fullname = document.querySelector('input[name="fullname"]').value.trim();
        const email = document.querySelector('input[name="email"]').value.trim();
        const password = document.querySelector('input[name="password"]').value.trim();

        if(fullname === ""){
            alert("Please enter your Full Name.");
            event.preventDefault();
            return;
        }

        const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

        if(!emailPattern.test(email)){
            alert("Please enter a valid Email Address.");
            event.preventDefault();
            return;
        }

        if(password.length < 8){
            alert("Please enter a valid Password.");
            event.preventDefault();
            return;
        }

        // Form will now submit to Django
    });

});