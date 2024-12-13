class SnippetGenerator {
    constructor(content, query, windowSize = 200) {
        this.content = content;
        this.query = query;
        this.windowSize = windowSize;
        this.queryTerms = this.preprocessQuery();
    }

    preprocessQuery() {
        return this.query
            .toLowerCase()
            .split(/\s+/)
            .filter(term => term.length > 2);
    }

    findBestSnippet() {
        const words = this.content.split(/\s+/);
        let bestScore = 0;
        let bestStart = 0;
        let bestEnd = Math.min(this.windowSize, words.length);

        // Slide window through content
        for (let i = 0; i <= words.length - this.windowSize; i++) {
            const windowWords = words.slice(i, i + this.windowSize);
            const score = this.calculateSnippetScore(windowWords);

            if (score > bestScore) {
                bestScore = score;
                bestStart = i;
                bestEnd = i + this.windowSize;
            }
        }

        return {
            text: words.slice(bestStart, bestEnd).join(' '),
            start: bestStart,
            end: bestEnd,
            score: bestScore
        };
    }

    calculateSnippetScore(words) {
        let score = 0;
        const windowText = words.join(' ').toLowerCase();

        for (const term of this.queryTerms) {
            const regex = new RegExp(term, 'gi');
            const matches = windowText.match(regex);
            if (matches) {
                score += matches.length;
            }
        }

        return score;
    }

    highlightTerms(text) {
        let highlightedText = text;
        for (const term of this.queryTerms) {
            const regex = new RegExp(`(${term})`, 'gi');
            highlightedText = highlightedText.replace(regex, '<span class="highlight">$1</span>');
        }
        return highlightedText;
    }

    generateSnippet() {
        const snippet = this.findBestSnippet();
        const highlightedSnippet = this.highlightTerms(snippet.text);
        return {
            html: `<div class="snippet-container">${highlightedSnippet}</div>`,
            text: snippet.text,
            score: snippet.score
        };
    }
}

function displayResultsGrid(docs) {
    const resultsDiv = document.getElementById('results');
    resultsDiv.innerHTML = '';

    docs.forEach(doc => {
        const snippetGenerator = new SnippetGenerator(
            doc.Content,
            document.getElementById('searchQuery').value
        );
        const snippet = snippetGenerator.generateSnippet();

        const card = document.createElement('div');
        card.className = 'result-card p-6';
        card.dataset.clusters = doc.clusters || '';

        card.innerHTML = `
            <div class="relative">
                <h2 class="text-xl font-bold text-gray-900 pr-20">${doc.Title}</h2>
                <div class="result-score">${doc.Score.toFixed(1)}</div>
            </div>
            ${doc.Subtitle ? `<div class="result-metadata">${doc.Subtitle}</div>` : ''}
            ${snippet.html}
            <div class="mt-4">
                ${(doc.clusters || []).map(cluster => 
                    `<span class="cluster-tag">${cluster}</span>`
                ).join('')}
            </div>
        `;

        resultsDiv.appendChild(card);
    });
}