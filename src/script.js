function geoFindMe() {
    const status = document.querySelector("#status");
    const mapLink = document.querySelector("#map-link");

    mapLink.href = "";
    mapLink.textContent = "";

    async function success(position) {
        const latitude = position.coords.latitude
        const longitude = position.coords.longitude
        const timestamp = position.timestamp

        status.textContent = "";
        mapLink.href = `https://www.openstreetmap.org/#map=18/${latitude}/${longitude}`;

        const address = await getAddressFromCoords(latitude, longitude);
        mapLink.textContent = address;

        sendLocationToBackend(latitude, longitude, timestamp);
    }

    function error() {
        status.textContent = "Unable to retrieve your location";
    }

    if (!navigator.geolocation) {
        status.textContent = "Geolocation is not supported by your browser";
    } else {
        status.textContent = "Locating...";
        navigator.geolocation.getCurrentPosition(success, error);
    }
}

async function getAddressFromCoords(latitude, longitude) {
    const url = `https://nominatim.openstreetmap.org/reverse?format=json&lat=${latitude}&lon=${longitude}`;
    try {
        const response = await fetch(url);
        const data = await response.json();
        return data.display_name;
    } catch (error) {
        console.error("Error fetching address:", error);
        return "Unable to retrieve address";
    }
}

function sendLocationToBackend(latitude, longitude, timestamp) {
    fetch("http://127.0.0.1:8000/api/save-location", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ latitude: latitude, longitude: longitude, timestamp: timestamp }),
    })
      .then((response) => {
        if (!response.ok) {
          throw new Error("Failed to save location");
        }
        return response.json();
      })
      .then((data) => {
        console.log("Location saved successfully:", data);
      })
      .catch((error) => {
        console.error("Error:", error);
      });
  }  
  
  document.querySelector("#find-me").addEventListener("click", geoFindMe);