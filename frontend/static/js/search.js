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
            
            const reviewModal = document.getElementById('reviewModal');
            const clusterModal = document.getElementById('clusterModal');
            if (!reviewModal || !clusterModal) {
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
                        <div class="text-sm">Published or Last Updated</div>
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
                <div id="similar-reviews-section" class="mt-8 pt-8 border-t border-gray-200">
                    <h3 class="text-xl font-bold text-gray-900 mb-4">Similar Games</h3>
                    <div id="similar-reviews" class="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div class="text-center text-gray-500">Loading similar games...</div>
                    </div>
                </div>
            `;
            
            // Show modal
            reviewModal.classList.remove('hidden');
            clusterModal.classList.add('hidden');
            try {
                const similarResponse = await fetch(`/more-like-this/${review.id}`);
                if (!similarResponse.ok) throw new Error('Failed to fetch similar reviews');
                
                const similarReviews = await similarResponse.json();
                const similarContainer = document.getElementById('similar-reviews');
                
                if (similarReviews.length > 0) {
                    similarContainer.innerHTML = similarReviews.map(similar => `
                        <div class="bg-white rounded-lg shadow-sm p-4 cursor-pointer hover:shadow-md transition-shadow"
                            onclick="showFullReview('${similar.id}')">
                            <div class="flex justify-between items-start mb-2">
                                <h4 class="font-bold text-gray-900">${similar.Title}</h4>
                                <span class="bg-indigo-100 text-indigo-800 rounded-full px-2 py-1 text-sm">
                                    ${similar.Score.toFixed(1)}
                                </span>
                            </div>
                            <p class="text-gray-600 text-sm line-clamp-2">${similar.Content.substring(0, 100)}...</p>
                        </div>
                    `).join('');
                } else {
                    similarContainer.innerHTML = '<div class="col-span-2 text-center text-gray-500">No similar games found</div>';
                }
            } catch (error) {
                console.error('Error loading similar reviews:', error);
                document.getElementById('similar-reviews').innerHTML = 
                    '<div class="col-span-2 text-center text-gray-500">Failed to load similar games</div>';
            }
            document.body.style.overflow = 'hidden';
        } catch (error) {
            console.error('Error fetching review:', error);
            showError('Failed to load review details');
        }
    };

    window.showCluster = async function(cluster_data, cluster_label) {
        const reviewModal = document.getElementById('reviewModal');
        const clusterModal = document.getElementById('clusterModal');
        if (!reviewModal || !clusterModal) {
            console.error('Modal element not found');
            return;
        }
        
        // Update title
        const titleElement = document.getElementById('clusterModalTitle');
        if (titleElement) {
            titleElement.textContent = cluster_label || '';
        }

        // Main content container
        const contentContainer = document.getElementById('clusterModalContent');
        if (!contentContainer) {
            console.error('Modal content container not found');
            return;
        }
                
        if (Object.keys(cluster_data).length > 0) {
            contentContainer.innerHTML = cluster_data.map(review => `
                <div class="bg-white rounded-lg shadow-sm p-4 cursor-pointer hover:shadow-md transition-shadow"
                    onclick="showFullReview('${review.id}')">
                    <div class="flex justify-between items-start mb-2">
                        <h4 class="font-bold text-gray-900">${review.Title}</h4>
                        <span class="bg-indigo-100 text-indigo-800 rounded-full px-2 py-1 text-sm">
                            ${review.Score.toFixed(1)}
                        </span>
                    </div>
                    <p class="text-gray-600 text-sm line-clamp-2">${review.Content.substring(0, 100)}...</p>
                </div>
            `).join('');
        } else {
            contentContainer.innerHTML = '<div class="col-span-2 text-center text-gray-500">Error. No cluster data.</div>';
        }
        
        // Show modal
        reviewModal.classList.add('hidden');
        clusterModal.classList.remove('hidden');
        document.body.style.overflow = 'hidden';
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
        
        // Get cluster titles
        for (const key in data.cluster_labels) {
            const title = data.cluster_labels[key].split(',')[0].trim()
            data.cluster_labels[key] = title.charAt(0).toUpperCase() + title.slice(1)
        }
    
        // Pass titles to docs
        for (const key in data.clusters)
            data.clusters[key].map(doc => doc.ClusterLabel = data.cluster_labels[key]);
    
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
                
                clusterCard.addEventListener('click', () => showCluster(docs, data.cluster_labels[clusterId]));
                clusterList.appendChild(clusterCard);
            });
            clustersDiv.classList.remove('hidden');
        } else {
            clustersDiv.classList.add('hidden');
        }
    
        // Display all results
        const allDocs = Object.values(data.clusters).flat();
        
        if (allDocs.length === 0) {
            resultsDiv.innerHTML = `
                <div class="col-span-full text-center py-12">
                    <div class="text-4xl text-gray-400 mb-4">🔍</div>
                    <h3 class="text-xl font-bold text-gray-700 mb-2">No Results Found</h3>
                    <p class="text-gray-600">Try adjusting your search terms or filters</p>
                </div>
            `;
            return;
        }
    
        // Change grid layout based on number of results
        if (allDocs.length === 1) {
            resultsDiv.className = 'flex justify-center items-start w-full';
        } else {
            resultsDiv.className = 'grid grid-cols-1 md:grid-cols-2 gap-6';
        }
        
        allDocs.forEach(doc => {
            const card = document.createElement('div');
            card.className = `result-card p-6 cursor-pointer hover:shadow-lg transition-all ${allDocs.length === 1 ? 'w-full max-w-2xl' : ''}`;
     
            card.innerHTML = `
                <div class="relative mb-6">
                    <h2 class="text-xl font-bold text-gray-900 mb-2 pr-24">${doc.Title}</h2>
                    <div class="absolute top-0 right-0">
                        <div class="bg-indigo-100 text-indigo-800 rounded-full px-3 py-1">
                            Score: ${doc.Score.toFixed(1)}
                        </div>
                    </div>
                </div>
                ${doc.Subtitle ? `<div class="text-gray-600 mb-4">${doc.Subtitle}</div>` : ''}
                <div class="text-gray-700 line-clamp-3 mb-4">${doc.Content.substring(0, 200)}...</div>
                <div class="flex justify-between items-center">
                    <div class="text-sm text-indigo-600 hover:text-indigo-800">Click to read full review</div>
                    <div class="bg-white text-gray-500 border-2 border-gray-300 rounded-full px-3 py-1 text-sm">
                        ${doc.ClusterLabel}
                    </div>
                </div>
            `;
            
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
        // clustersDiv.classList.add('hidden');
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

    // Make closeClusterModal available globally
    window.closeClusterModal = function() {
        document.getElementById('clusterModal').classList.add('hidden');
        document.body.style.overflow = 'auto';
    };

    // Close modal when clicking outside
    document.getElementById('clusterModal').addEventListener('click', (e) => {
        if (e.target === document.getElementById('clusterModal')) {
            closeClusterModal();
        }
    });
});