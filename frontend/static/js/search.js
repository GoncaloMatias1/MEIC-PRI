document.addEventListener('DOMContentLoaded', function() {
    const searchButton = document.getElementById('searchButton');
    const searchInput = document.getElementById('searchQuery');
    const loadingDiv = document.getElementById('loading');
    const clustersDiv = document.getElementById('clusters');
    const clusterList = document.getElementById('cluster-list');
    
    // Make showFullReview globally available
    window.showFullReview = async function(reviewId) {
        try {
            const response = await fetch(`/review/${reviewId}`);
            if (!response.ok) throw new Error('Failed to fetch review');
            
            const review = await response.json();
            const modal = document.getElementById('reviewModal');
            
            if (!modal) {
                console.error('Modal element not found');
                return;
            }
    
            // Extract date and author from Subheader
            let publishDate = 'Date not available';
            let author = 'Unknown author';
            let publisher = 'IGN';
            
            if (review.Subheader) {
                const dateMatch = review.Subheader.match(/Updated: ([A-Za-z]+ \d+, \d{4})/);
                if (dateMatch) {
                    publishDate = dateMatch[1];
                }
                
                const authorMatch = review.Subheader.match(/By ([^,]+)/);
                if (authorMatch) {
                    author = authorMatch[1].trim();
                }
            }
    
            // Detect platforms from content
            const platforms = detectPlatformsFromContent(review.Content || '');
            
            // Update title
            const titleElement = document.getElementById('modalTitle');
            if (titleElement) {
                titleElement.textContent = review.Title || '';
            }
    
            // Main content container
            const contentContainer = document.getElementById('modalContent');
            if (!contentContainer) {
                console.error('Modal content container not found');
                return;
            }
    
            // Build the modal content
            contentContainer.innerHTML = `
                <div class="review-metadata">
                    <div class="metadata-item">
                        <div class="text-sm">Score</div>
                        <div class="text-lg score-highlight">${review.Score ? review.Score.toFixed(1) : 'N/A'}</div>
                    </div>
                    <div class="metadata-item">
                        <div class="text-sm">Published</div>
                        <div class="text-md">${publishDate}</div>
                    </div>
                    <div class="metadata-item">
                        <div class="text-sm">Author</div>
                        <div class="text-md">${author}</div>
                    </div>
                    <div class="metadata-item">
                        <div class="text-sm">Publisher</div>
                        <div class="text-md">${publisher}</div>
                    </div>
                    ${platforms.length > 0 ? `
                        <div class="metadata-item col-span-full">
                            <div class="text-sm">Platforms</div>
                            <div class="platform-tags">
                                ${platforms.map(platform => `
                                    <span class="platform-tag">${platform}</span>
                                `).join('')}
                            </div>
                        </div>
                    ` : ''}
                </div>
                ${review.Subtitle ? `<div class="review-subtitle">${review.Subtitle}</div>` : ''}
                <div class="review-content">
                    ${review.Content || 'No content available'}
                </div>
            `;
            
            // Show modal
            modal.classList.remove('hidden');
            document.body.style.overflow = 'hidden';
        } catch (error) {
            console.error('Error fetching review:', error);
            showError('Failed to load review details');
        }
    };
    
    // Fetch and display latest reviews on page load
    async function fetchLatestReviews() {
        try {
            const response = await fetch('/latest');
            const reviews = await response.json();
            
            const latestContainer = document.getElementById('latest-reviews');
            if (!latestContainer) return;
            
            latestContainer.innerHTML = reviews.map(review => {
                // Extract the date from Subheader
                let publishDate = 'Recent';
                if (review.Subheader) {
                    const dateMatch = review.Subheader.match(/Updated: ([A-Za-z]+ \d+, \d{4})/);
                    if (dateMatch) {
                        publishDate = dateMatch[1];
                    }
                }
                
                return `
                    <div class="bg-white rounded-xl shadow-lg p-6 hover:shadow-xl transition-all cursor-pointer"
                         onclick="showFullReview('${review.id}')">
                        <div class="relative mb-4">
                            <span class="absolute top-0 right-0 bg-green-100 text-green-600 px-3 py-1 rounded-full text-sm font-medium">
                                Score: ${review.Score.toFixed(1)}
                            </span>
                        </div>
                        <div class="text-sm text-gray-500 mb-2">${publishDate}</div>
                        <h4 class="text-xl font-bold text-gray-900 mb-3">${review.Title}</h4>
                        <p class="text-gray-600 line-clamp-3">
                            ${review.Content.substring(0, 150)}...
                        </p>
                        <div class="mt-4 text-sm text-indigo-600 hover:text-indigo-800">
                            Read full review →
                        </div>
                    </div>
                `;
            }).join('');
            
        } catch (error) {
            console.error('Error fetching latest reviews:', error);
        }
    }

    // Call it when page loads
    fetchLatestReviews();
    
    function displayResults(data) {
        const resultsDiv = document.getElementById('results');
        const clustersDiv = document.getElementById('clusters');
        
        // Clear previous results
        resultsDiv.innerHTML = '';
        clusterList.innerHTML = '';
        
        // Hide latest reviews section
        document.getElementById('trending-section').classList.add('hidden');
        
        // Display clusters
        if (Object.keys(data.clusters).length > 1) {
            Object.entries(data.clusters).forEach(([clusterId, docs]) => {
                const clusterCard = document.createElement('div');
                clusterCard.className = 'cluster-card';
                
                clusterCard.innerHTML = `
                    <div class="cluster-label">${data.cluster_labels[clusterId]}</div>
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

    function detectPlatformsFromContent(content) {
        const platformPatterns = {
            'PS5': /\b(PS5|PlayStation 5)\b/i,
            'PS4': /\b(PS4|PlayStation 4)\b/i,
            'PS3': /\b(PS3|PlayStation 3)\b/i,
            'Xbox Series X|S': /\b(Xbox Series X|Series X|Series S|Xbox Series)\b/i,
            'Xbox One': /\bXbox One\b/i,
            'Xbox 360': /\bXbox 360\b/i,
            'Nintendo Switch': /\b(Nintendo Switch|Switch)\b/i,
            'PC': /\b(PC|Windows|Steam)\b/i,
            'Wii U': /\bWii U\b/i,
            'Nintendo 3DS': /\b(3DS|Nintendo 3DS)\b/i,
            'Mobile': /\b(iOS|Android|iPhone|iPad|Mobile)\b/i
        };

        const foundPlatforms = new Set();
        
        for (const [platform, pattern] of Object.entries(platformPatterns)) {
            if (pattern.test(content)) {
                foundPlatforms.add(platform);
            }
        }
        
        return Array.from(foundPlatforms);
    }
    
    async function performSearch() {
        const query = searchInput.value.trim();
        const searchType = document.getElementById('searchType').value;
        const category = document.getElementById('searchCategory').value;
        const minScore = document.getElementById('minScore').value;
        
        // Only require query if no category is selected
        if (!query && category === 'all') {
            showError('Please enter a search term or select a category');
            return;
        }
        
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
                    category: category,
                    minScore: minScore || null
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

    // Close modal when clicking outside
    document.getElementById('reviewModal').addEventListener('click', (e) => {
        if (e.target === document.getElementById('reviewModal')) {
            closeReviewModal();
        }
    });
});