async function scheduleMeeting() {
    const data = {
        topic: document.getElementById('topic').value,
        start_time: document.getElementById('start_time').value,
        duration: parseInt(document.getElementById('duration').value),
        access_token: document.getElementById('access_token').value
    };

    const responseDiv = document.getElementById("response");
    responseDiv.innerHTML = "Scheduling meeting...";

    try {
        const response = await fetch("https://automated-meeting-schedular.onrender.com/schedule-meeting/", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(data)
        });

        const result = await response.json();
        
        if (response.ok) {
            responseDiv.innerHTML = `Meeting scheduled successfully! Meeting ID: ${result.id}`;
        } else {
            responseDiv.innerHTML = `Error: ${result.error.message}`;
        }
    } catch (error) {
        responseDiv.innerHTML = `Error: ${error.message}`;
    }
}

// Example usage
document.getElementById('schedule_button').addEventListener('click', scheduleMeeting);
