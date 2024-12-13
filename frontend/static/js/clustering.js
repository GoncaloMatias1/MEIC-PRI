function displayResults(data) {
    const clustersDiv = document.getElementById('clusters');
    const clusterList = document.getElementById('cluster-list');
    const resultsDiv = document.getElementById('results');
    
    // Clear previous results
    clusterList.innerHTML = '';
    resultsDiv.innerHTML = '';
    
    // Display clusters
    Object.entries(data.clusters).forEach(([clusterId, docs]) => {
        const clusterLabel = data.cluster_labels[clusterId];
        const clusterCard = createClusterCard(clusterLabel, docs);
        clusterList.appendChild(clusterCard);
    });
    
    // Show clusters section
    clustersDiv.classList.remove('hidden');
    
    // Display all results in the main grid
    const allDocs = Object.values(data.clusters).flat();
    displayResultsGrid(allDocs);
}

function createClusterCard(label, docs) {
    const div = document.createElement('div');
    div.className = 'cluster-card';
    
    div.innerHTML = `
        <div class="cluster-label">${label}</div>
        <div class="text-sm text-gray-600">
            ${docs.length} results
        </div>
        <div class="mt-2">
            <button class="text-indigo-600 hover:text-indigo-800 text-sm font-medium"
                    onclick="filterResultsByCluster('${label}')">
                Show these results
            </button>
        </div>
    `;
    
    return div;
}

function filterResultsByCluster(label) {
    const resultsDiv = document.getElementById('results');
    const cards = resultsDiv.querySelectorAll('.result-card');
    
    cards.forEach(card => {
        if (card.dataset.clusters.includes(label)) {
            card.classList.remove('hidden');
        } else {
            card.classList.add('hidden');
        }
    });
}