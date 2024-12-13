document.addEventListener('DOMContentLoaded', function() {
    const searchButton = document.getElementById('searchButton');
    const searchInput = document.getElementById('searchQuery');
    const loadingDiv = document.getElementById('loading');
    const clustersDiv = document.getElementById('clusters');
    const clusterList = document.getElementById('cluster-list');
    
    function displayResults(data) {
        const resultsDiv = document.getElementById('results');
        const clustersDiv = document.getElementById('clusters');
        
        // Clear previous results
        resultsDiv.innerHTML = '';
        clusterList.innerHTML = '';
        
        // Display clusters
        if (Object.keys(data.clusters).length > 1) {
            Object.entries(data.clusters).forEach(([clusterId, docs]) => {
                const clusterLabel = data.cluster_labels[clusterId];
                const clusterCard = document.createElement('div');
                clusterCard.className = 'cluster-card';
                
                clusterCard.innerHTML = `
                    <div class="cluster-label">${clusterLabel}</div>
                    <div class="text-sm text-gray-600">
                        ${docs.length} results
                    </div>
                `;
                
                clusterList.appendChild(clusterCard);
            });
            clustersDiv.classList.remove('hidden');
        } else {
            clustersDiv.classList.add('hidden');
        }
        
        // Display all results
        const allDocs = Object.values(data.clusters).flat();
        
        allDocs.forEach(doc => {
            const card = document.createElement('div');
            card.className = 'result-card p-6 cursor-pointer hover:shadow-lg transition-all';
            
            card.innerHTML = `
                <div class="relative">
                    <h2 class="text-xl font-bold text-gray-900 mb-2">${doc.Title}</h2>
                    <div class="absolute top-0 right-0 bg-indigo-100 text-indigo-800 rounded-full px-3 py-1">
                        Score: ${doc.Score.toFixed(1)}
                    </div>
                </div>
                ${doc.Subtitle ? `<div class="text-gray-600 mb-4">${doc.Subtitle}</div>` : ''}
                <div class="text-gray-700 line-clamp-3 mb-4">${doc.Content.substring(0, 200)}...</div>
                <div class="text-sm text-indigo-600 hover:text-indigo-800">Click to read full review</div>
            `;
            
            // Add click event listener
            card.addEventListener('click', () => showFullReview(doc.id));
            
            resultsDiv.appendChild(card);
        });
    }
    
    async function showFullReview(reviewId) {
        try {
            const response = await fetch(`/review/${reviewId}`);
            if (!response.ok) throw new Error('Failed to fetch review');
            
            const review = await response.json();
            const modal = document.getElementById('reviewModal');
            
            document.getElementById('modalTitle').textContent = review.Title;
            document.getElementById('modalContent').innerHTML = `
                ${review.Subtitle ? `<div class="text-gray-600 mb-4">${review.Subtitle}</div>` : ''}
                <div class="inline-block bg-indigo-100 text-indigo-800 rounded-lg px-4 py-2 mb-6">
                    Score: ${review.Score.toFixed(1)}
                </div>
                <div class="text-gray-700 whitespace-pre-wrap">${review.Content}</div>
            `;
            
            modal.classList.remove('hidden');
            document.body.style.overflow = 'hidden';
        } catch (error) {
            console.error('Error fetching review:', error);
        }
    }
    
    async function performSearch() {
        const query = searchInput.value;
        const searchType = document.getElementById('searchType').value;
        const category = document.getElementById('searchCategory').value;
        
        if (!query) return;
        
        showLoading(true);
        
        try {
            const response = await fetch('/search', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    query: query,
                    searchType: searchType,
                    category: category
                })
            });
            
            const data = await response.json();
            if (data.error) {
                showError(data.error);
            } else {
                displayResults(data);
            }
        } catch (error) {
            console.error('Search error:', error);
            showError('Error performing search. Please try again.');
        } finally {
            showLoading(false);
        }
    }
    
    function showLoading(show) {
        loadingDiv.classList.toggle('hidden', !show);
        clustersDiv.classList.add('hidden');
    }
    
    function showError(message) {
        const resultsDiv = document.getElementById('results');
        resultsDiv.innerHTML = `
            <div class="col-span-full text-center text-red-600 bg-red-50 rounded-lg p-4">
                ${message}
            </div>
        `;
    }
    
    // Event listeners
    searchButton.addEventListener('click', performSearch);
    searchInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') performSearch();
    });
    
    // Make closeReviewModal available globally
    window.closeReviewModal = function() {
        document.getElementById('reviewModal').classList.add('hidden');
        document.body.style.overflow = 'auto';
    };
});