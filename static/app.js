// Application logic - Agri-Assistant

document.addEventListener('DOMContentLoaded', () => {
    const btnAnalyze = document.getElementById('btn-analyze');
    const btnReset = document.getElementById('btn-reset');
    const actionSection = document.getElementById('action-section');
    const loadingSection = document.getElementById('loading-section');
    const resultsSection = document.getElementById('results-section');
    const btnText = btnAnalyze.querySelector('.btn-text');
    const btnLoader = btnAnalyze.querySelector('.btn-loader');
    
    // UI Elements for results
    const badgeSoilType = document.getElementById('badge-soil-type');
    const badgePh = document.getElementById('badge-ph');
    const badgeFertility = document.getElementById('badge-fertility');
    const cropsContainer = document.getElementById('crops-container');
    
    // API URL
    const API_URL = '/api/v1/recommend';

    // Event Listeners
    btnAnalyze.addEventListener('click', startAnalysis);
    btnReset.addEventListener('click', resetUI);

    /**
     * Start the analysis process (Geolocation -> API Call -> Render)
     */
    function startAnalysis() {
        if (!navigator.geolocation) {
            showError("Votre navigateur ne supporte pas la geolocalisation.");
            return;
        }

        // Show loading state on button
        btnText.style.display = 'none';
        btnLoader.style.display = 'block';
        btnAnalyze.disabled = true;

        navigator.geolocation.getCurrentPosition(
            async (position) => {
                const lat = position.coords.latitude;
                const lon = position.coords.longitude;
                
                // Transition to loading radar screen
                actionSection.style.display = 'none';
                loadingSection.style.display = 'flex';
                
                try {
                    const data = await fetchRecommendations(lat, lon);
                    renderResults(data);
                } catch (error) {
                    resetUI();
                    showError(error.message || "Erreur lors de l'analyse.");
                }
            },
            (error) => {
                resetUI();
                if (error.code === error.PERMISSION_DENIED) {
                    showError("Vous devez autoriser le GPS pour l'analyse.");
                } else {
                    showError("Impossible d'obtenir votre position GPS.");
                }
            },
            { enableHighAccuracy: true, timeout: 10000, maximumAge: 0 }
        );
    }

    /**
     * Fetch data from the FastAPI Backend
     */
    async function fetchRecommendations(lat, lon) {
        document.getElementById('loading-text').textContent = "Analyse agronomique...";
        
        const response = await fetch(API_URL, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ latitude: lat, longitude: lon })
        });

        if (!response.ok) {
            const err = await response.json();
            throw new Error(err.detail || "Le serveur est indisponible.");
        }

        return await response.json();
    }

    /**
     * Render the UI with API data
     */
    function renderResults(data) {
        // Hide loading, show results
        loadingSection.style.display = 'none';
        resultsSection.style.display = 'flex';

        // Update Soil Badges
        if (data.soil_summary) {
            badgeSoilType.textContent = `Sol: ${data.soil_summary.soil_type}`;
            badgePh.textContent = `pH: ${data.soil_summary.ph}`;
            badgeFertility.textContent = `Fertilite: ${data.soil_summary.fertility}`;
        }

        // Clear previous crops
        cropsContainer.innerHTML = '';

        // Render Crops
        if (data.recommendations && data.recommendations.length > 0) {
            data.recommendations.forEach(rec => {
                const card = document.createElement('div');
                card.className = `crop-card rank-${rec.rank}`;
                
                const scorePercent = Math.round(rec.confidence * 100);
                
                // Separate the advice from normal reasons
                const normalReasons = rec.reasons.filter(r => !r.startsWith('Nous sommes en'));
                const advice = rec.reasons.find(r => r.startsWith('Nous sommes en'));

                let reasonsHTML = `<ul class="crop-reasons">`;
                normalReasons.forEach(r => {
                    reasonsHTML += `<li>${r}</li>`;
                });
                reasonsHTML += `</ul>`;

                let adviceHTML = '';
                if (advice) {
                    adviceHTML = `<div class="crop-advice">ℹ️ ${advice}</div>`;
                }

                card.innerHTML = `
                    <div class="crop-header">
                        <div class="crop-name">
                            <span class="crop-rank">${rec.rank}</span>
                            ${rec.crop}
                        </div>
                        <div class="crop-score">${scorePercent}%</div>
                    </div>
                    ${reasonsHTML}
                    ${adviceHTML}
                `;
                
                cropsContainer.appendChild(card);
            });
        } else {
            cropsContainer.innerHTML = `
                <div class="glass-card" style="text-align: center;">
                    <p>Aucune culture n'est viablé actuellement pour votre sol.</p>
                </div>
            `;
        }
    }

    /**
     * Reset the UI to initial state
     */
    function resetUI() {
        resultsSection.style.display = 'none';
        loadingSection.style.display = 'none';
        actionSection.style.display = 'block';
        
        btnText.style.display = 'block';
        btnLoader.style.display = 'none';
        btnAnalyze.disabled = false;
        
        document.getElementById('loading-text').textContent = "Geolocalisation en cours...";
    }

    /**
     * Show a toast error message
     */
    function showError(message) {
        const toast = document.getElementById('error-toast');
        toast.textContent = message;
        toast.classList.add('show');
        
        setTimeout(() => {
            toast.classList.remove('show');
        }, 4000);
    }
});
