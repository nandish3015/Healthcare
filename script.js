document.addEventListener('DOMContentLoaded', () => {
    const uploadArea = document.getElementById('upload-area');
    const imageUpload = document.getElementById('image-upload');
    const scanButton = document.getElementById('scan-button');
    const resultsSection = document.getElementById('results');
    const profileForm = document.getElementById('profile-form');

    // Handle profile form submission
    profileForm.addEventListener('submit', (e) => {
        e.preventDefault();
        alert('Profile saved! (Simulated)');
        // In production, send to backend or store locally
    });

    // Handle image upload
    uploadArea.addEventListener('click', () => imageUpload.click());
    uploadArea.addEventListener('dragover', (e) => {
        e.preventDefault();
        uploadArea.style.backgroundColor = '#e0e0e0';
    });
    uploadArea.addEventListener('dragleave', () => {
        uploadArea.style.backgroundColor = 'white';
    });
    uploadArea.addEventListener('drop', (e) => {
        e.preventDefault();
        uploadArea.style.backgroundColor = 'white';
        const file = e.dataTransfer.files[0];
        if (file && file.type.startsWith('image/')) {
            imageUpload.files = e.dataTransfer.files;
            scanButton.disabled = false;
        }
    });

    imageUpload.addEventListener('change', () => {
        if (imageUpload.files.length > 0) {
            scanButton.disabled = false;
        }
    });

    // Handle scan button
    scanButton.addEventListener('click', async () => {
        const formData = new FormData();
        formData.append('image', imageUpload.files[0]);

        try {
            const response = await fetch('http://127.0.0.1:5000/scan', {
                method: 'POST',
                body: formData
            });
            const data = await response.json();

            // Display results
            resultsSection.hidden = false;
            document.getElementById('score').textContent = `Score: ${data.analysis.score}`;
            document.getElementById('score').className = `score ${data.analysis.score.toLowerCase()}`;

            const nutritionList = document.getElementById('nutrition');
            nutritionList.innerHTML = '';
            for (const [key, value] of Object.entries(data.nutrition)) {
                if (key !== 'allergens') {
                    nutritionList.innerHTML += `<li>${key}: ${value}</li>`;
                }
            }
            if (data.nutrition.allergens.length) {
                nutritionList.innerHTML += `<li>Allergens: ${data.nutrition.allergens.join(', ')}</li>`;
            }

            const ingredientsList = document.getElementById('ingredients');
            ingredientsList.innerHTML = data.ingredients.map(i => `<li>${i}</li>`).join('');

            document.getElementById('warnings').textContent = data.analysis.warnings.join('; ') || 'None';
            document.getElementById('suggestions').textContent = data.analysis.suggestions.join('; ') || 'None';
        } catch (error) {
            alert('Error scanning label: ' + error.message);
        }
    });
});