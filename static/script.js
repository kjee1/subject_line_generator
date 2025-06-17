document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('headlineForm');
    const resultsDiv = document.getElementById('results');
    const headlinesList = document.getElementById('headlinesList');
    const loadingDiv = document.getElementById('loading');

    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        // Show loading spinner
        loadingDiv.classList.remove('hidden');
        resultsDiv.classList.add('hidden');
        headlinesList.innerHTML = '';

        const formData = {
            newsletter_text: document.getElementById('newsletterText').value,
            audience_profile: document.getElementById('audienceProfile').value || "",
            goal: document.getElementById('goal').value || "",
            tone: document.getElementById('tone').value,
            provider: document.getElementById('provider').value,
            model: document.getElementById('provider').value === 'openai' ? 'gpt-4' : 
                   document.getElementById('provider').value === 'anthropic' ? 'claude-3-opus-20240229' : 'gemini-pro',
            past_headlines: [],
            constraints: {
                max_length: 60,
                avoid_clickbait: true,
                require_numbers: false
            }
        };

        try {
            console.log('Sending request with data:', formData);
            const response = await fetch('/generate', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(formData)
            });

            console.log('Response status:', response.status);
            const responseText = await response.text();
            console.log('Response text:', responseText);

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}, message: ${responseText}`);
            }

            const data = JSON.parse(responseText);
            console.log('Parsed response data:', data);
            
            if (!data.headlines || !Array.isArray(data.headlines)) {
                throw new Error('Invalid response format: missing headlines array');
            }

            displayResults(data.headlines);
        } catch (error) {
            console.error('Error:', error);
            headlinesList.innerHTML = `
                <div class="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative" role="alert">
                    <strong class="font-bold">Error!</strong>
                    <span class="block sm:inline"> ${error.message}</span>
                </div>
            `;
        } finally {
            loadingDiv.classList.add('hidden');
            resultsDiv.classList.remove('hidden');
        }
    });

    function displayResults(headlines) {
        if (!headlines || headlines.length === 0) {
            headlinesList.innerHTML = `
                <div class="bg-yellow-100 border border-yellow-400 text-yellow-700 px-4 py-3 rounded relative" role="alert">
                    <strong class="font-bold">No headlines generated.</strong>
                    <span class="block sm:inline"> Please try again with different input.</span>
                </div>
            `;
            return;
        }

        headlinesList.innerHTML = headlines.map(headline => `
            <div class="bg-white rounded-lg shadow-md p-6 headline-card">
                <h3 class="text-xl font-semibold text-gray-800 mb-3">${headline.title}</h3>
                <div class="mb-3">
                    ${headline.keywords.map(keyword => `
                        <span class="keyword-tag">${keyword}</span>
                    `).join('')}
                </div>
                <p class="reason-text">${headline.reason}</p>
            </div>
        `).join('');
    }
}); 