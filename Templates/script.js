// Populate dropdowns for drivers and circuits
async function populateDropdowns() {
    try {
        // Fetch drivers from Flask backend
        const driverResponse = await fetch('http://127.0.0.1:5000/drivers');
        const driverData = await driverResponse.json();
        const driverSelect = document.getElementById('driver');
        
        // Loop over the driver data and create options for the dropdown
        Object.keys(driverData).forEach(driver => {
            const option = document.createElement('option');
            option.value = driver; // Use family name as the value
            option.textContent = `${driverData[driver].firstName} ${driverData[driver].lastName}`; // Display first + last name
            driverSelect.appendChild(option);
        });

        // Fetch circuits from Flask backend
        const circuitResponse = await fetch('http://127.0.0.1:5000/circuits');
        const circuitData = await circuitResponse.json();
        const circuitSelect = document.getElementById('circuit');
        
        // Loop over the circuit data and create options for the dropdown
        Object.keys(circuitData).forEach(circuit => {
            const option = document.createElement('option');
            option.value = circuit; // Use circuit name as value
            option.textContent = circuit; // Display circuit name
            circuitSelect.appendChild(option);
        });
    } catch (error) {
        console.error('Error fetching dropdown data:', error);
        alert('Failed to load driver and circuit data. Please try again.');
    }
}
populateDropdowns();

// Handle form submission for prediction
document.getElementById('prediction-form').addEventListener('submit', async (e) => {
    e.preventDefault();

    // Get form data
    const driver = document.getElementById('driver').value;
    const circuit = document.getElementById('circuit').value;
    const qualifyingPosition = document.getElementById('qualifying_position').value.trim();

    // Validate inputs
    if (!driver || !circuit || !qualifyingPosition) {
        alert('Please fill in all fields.');
        return;
    }

    try {
        // Make API request to Flask backend with POST method
        const response = await fetch('http://127.0.0.1:5000/predict', {
            method: 'POST', // Ensure this is POST
            headers: {
                'Content-Type': 'application/json'  
            },
            body: JSON.stringify({
                Driver: driver,
                Circuit: circuit,
                Qualifying_Position: parseInt(qualifyingPosition, 10)
            })
        });

        if (!response.ok) {
            throw new Error('Failed to fetch prediction');
        }

        const data = await response.json();
        const resultDiv = document.getElementById('result');
        resultDiv.innerHTML = `🏆 Winning Probability: <strong>${data.win_probability}%</strong>`;
    } catch (error) {
        document.getElementById('result').innerHTML = 'Prediction failed. Please try again.';
    }
});
