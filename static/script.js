document.addEventListener("DOMContentLoaded", function() {
    fetch("/get_locations")
        .then(response => response.json())
        .then(data => {
            let pickupSelect = document.getElementById("pickup_location");
            let dropSelect = document.getElementById("drop_location");

            data.forEach(location => {
                let option1 = new Option(location, location);
                let option2 = new Option(location, location);
                pickupSelect.add(option1);
                dropSelect.add(option2);
            });
        })
        .catch(error => console.error("Error fetching locations:", error));

    function updateClock() {
        let now = new Date();
        let hours = now.getHours().toString().padStart(2, '0');
        let minutes = now.getMinutes().toString().padStart(2, '0');
        let seconds = now.getSeconds().toString().padStart(2, '0');
        document.getElementById("live-clock").textContent = `${hours}:${minutes}:${seconds}`;
    }

    setInterval(updateClock, 1000);
    updateClock();
});

function getETA() {
    const pickup_location = document.getElementById("pickup_location").value;
    const drop_location = document.getElementById("drop_location").value;
    const weather_input = document.getElementById("weather_input").value;
    const special_event = document.getElementById("special_event").value;

    if (!pickup_location || !drop_location) {
        alert("Please select pickup and drop locations.");
        return;
    }

    fetch("/predict_eta", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            pickup_location,
            drop_location,
            weather_input,
            special_event
        })
    })
    .then(response => response.json())
    .then(data => {
        document.getElementById("eta_result").textContent = `ETA: ${data.predicted_eta_minutes} minutes`;
    })
    .catch(error => console.error("Error:", error));
}

function checkSurge() {
    const pickup_location = document.getElementById("pickup_location").value;
    const drop_location = document.getElementById("drop_location").value;
    const weather_input = document.getElementById("weather_input").value;
    const special_event = document.getElementById("special_event").value;

    if (!pickup_location || !drop_location) {
        alert("Please select pickup and drop locations.");
        return;
    }

    fetch("/predict_surge", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            pickup_location,
            drop_location,
            weather_input,
            special_event
        })
    })
    .then(response => response.json())
    .then(data => {
        const alertBox = document.getElementById("surge_alert");
        alertBox.style.display = "block";

        let conf = "--";
        if (typeof data.confidence === "number" && !isNaN(data.confidence)) {
            conf = (data.confidence * 100).toFixed(2);
        }

        if (data.is_surge === 1) {
            if (data.confidence >= 0.8) {
                alertBox.className = "surge-alert surge-red";
                alertBox.textContent = `Surge Active! (Confidence: ${conf}%)`;
            } else {
                alertBox.className = "surge-alert surge-yellow";
                alertBox.textContent = ` Possible Surge (Confidence: ${conf}%)`;
            }
        } else {
            alertBox.className = "surge-alert surge-green";
            alertBox.textContent = ` No Surge (Confidence: ${conf}%)`;
        }
    })
    .catch(error => console.error("Error:", error));
}



