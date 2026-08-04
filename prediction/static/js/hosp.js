const locationBtn = document.getElementById("locationBtn");
const searchBtn = document.getElementById("searchBtn");
const locationInput = document.getElementById("locationInput");
const hospitalContainer = document.getElementById("hospitalContainer");


// -----------------------------
// Get CSRF Token
// -----------------------------

function getCookie(name) {

    let cookieValue = null;

    if (document.cookie && document.cookie !== "") {

        const cookies = document.cookie.split(";");

        for (let i = 0; i < cookies.length; i++) {

            const cookie = cookies[i].trim();

            if (cookie.substring(0, name.length + 1) === (name + "=")) {

                cookieValue = decodeURIComponent(
                    cookie.substring(name.length + 1)
                );

                break;
            }
        }
    }

    return cookieValue;
}

const csrftoken = getCookie("csrftoken");


// -----------------------------
// Current Location
// -----------------------------

locationBtn.addEventListener("click", function () {

    if (!navigator.geolocation) {

        alert("Geolocation not supported.");

        return;
    }

    navigator.geolocation.getCurrentPosition(

        function (position) {

            sendLocation({

                latitude: position.coords.latitude,

                longitude: position.coords.longitude

            });

        },

        function () {

            alert("Location permission denied.\nPlease enter your City / Area / Pincode.");

            locationInput.focus();

        }

    );

});


// -----------------------------
// Manual Search
// -----------------------------

searchBtn.addEventListener("click", function () {

    let location = locationInput.value.trim();

    if (location === "") {

        alert("Please enter your location.");

        return;

    }

    sendLocation({

        location: location

    });

});


// -----------------------------
// Send Data To Django
// -----------------------------

function sendLocation(data) {

    hospitalContainer.innerHTML =
    "<h3>Searching nearby hospitals...</h3>";

    fetch("/nearby-hospitals/",  {

        method: "POST",

        headers: {

            "Content-Type": "application/json",

            "X-CSRFToken": csrftoken

        },

        body: JSON.stringify(data)

    })

    .then(response => response.json())

    .then(result => {

        displayHospitals(result);

    })

    .catch(error => {

        console.log(error);

        hospitalContainer.innerHTML =
        "<h3>Something went wrong.</h3>";

    });

}


// -----------------------------
// Display Hospitals
// -----------------------------

function displayHospitals(hospitals) {

    hospitalContainer.innerHTML = "";

    if (hospitals.error) {

        hospitalContainer.innerHTML =
        `<h3>${hospitals.error}</h3>`;

        return;

    }

    if (hospitals.length === 0) {

        hospitalContainer.innerHTML =
        "<h3>No nearby psychologists or psychiatrists found.</h3>";

        return;

    }

    hospitals.forEach(function (hospital) {

        let card = document.createElement("div");

        card.className = "hospital-card";

        card.innerHTML = `

            <h2>${hospital.name}</h2>

            <p><strong>Address:</strong> ${hospital.address}</p>

            <p><strong>Phone:</strong> ${hospital.phone}</p>

            <div class="btn-group">

                <a href="${hospital.maps}"
                   target="_blank"
                   class="mapBtn">

                   View on Maps

                </a>

                <a href="${hospital.direction}"
                   target="_blank"
                   class="directionBtn">

                   Get Directions

                </a>

            </div>

        `;

        hospitalContainer.appendChild(card);

    });

}