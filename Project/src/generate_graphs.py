import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import re
from datetime import datetime
from collections import Counter
from calendar import month_abbr

data_path = 'webscrapper_out/ign.csv'
df = pd.read_csv(data_path)

def safe_plot(plot_func, filename):
    try:
        plot_func()
        plt.savefig(f'../docs/{filename}.png')
        plt.close()
        print(f"Generated {filename}.png")
    except Exception as e:
        print(f"Error generating {filename}.png: {str(e)}")
    finally:
        plt.close()

# 1. Score Distribution
def plot_score_distribution():
    plt.figure(figsize=(10, 6))
    sns.histplot(df['Score'], bins=20, kde=True)
    plt.title('Distribution of Game Scores')
    plt.xlabel('Score')
    plt.ylabel('Frequency')

safe_plot(plot_score_distribution, 'score_distribution')

# 2. Content Length vs Score
def plot_content_length_vs_score():
    df['Content Length'] = df['Content'].str.len()
    plt.figure(figsize=(10, 6))
    sns.scatterplot(x='Content Length', y='Score', data=df)
    plt.title('Review Content Length vs Score')
    plt.xlabel('Content Length (characters)')
    plt.ylabel('Score')

safe_plot(plot_content_length_vs_score, 'content_length_vs_score')

# 3. Top 10 Highest Scored Games
def plot_top_10_games():
    top_10 = df.nlargest(10, 'Score')
    plt.figure(figsize=(12, 6))
    sns.barplot(x='Score', y='Title', data=top_10)
    plt.title('Top 10 Highest Scored Games')
    plt.xlabel('Score')
    plt.ylabel('Game Title')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()

safe_plot(plot_top_10_games, 'top_10_games')

# 4. Distribution of Subtitle Lengths
def plot_subtitle_length_distribution():
    df['Subtitle Length'] = df['Subtitle'].str.len()
    plt.figure(figsize=(10, 6))
    sns.histplot(df['Subtitle Length'], bins=20, kde=True)
    plt.title('Distribution of Subtitle Lengths')
    plt.xlabel('Subtitle Length (characters)')
    plt.ylabel('Frequency')

safe_plot(plot_subtitle_length_distribution, 'subtitle_length_distribution')

# 5. Subheader Word Count vs Score
def plot_subheader_wordcount_vs_score():
    df['Subheader Word Count'] = df['Subheader'].str.split().str.len()
    plt.figure(figsize=(10, 6))
    sns.scatterplot(x='Subheader Word Count', y='Score', data=df)
    plt.title('Subheader Word Count vs Score')
    plt.xlabel('Subheader Word Count')
    plt.ylabel('Score')

safe_plot(plot_subheader_wordcount_vs_score, 'subheader_wordcount_vs_score')

# 6. Score distribution by title word count
def plot_score_by_title_length():
    df['Title Word Count'] = df['Title'].str.split().str.len()
    plt.figure(figsize=(12, 6))
    sns.boxplot(x='Title Word Count', y='Score', data=df)
    plt.title('Score Distribution by Title Word Count')
    plt.xlabel('Number of Words in Title')
    plt.ylabel('Score')

safe_plot(plot_score_by_title_length, 'score_by_title_length')

# 7. Review month analysis
def plot_score_by_month():
    def extract_date(date_string):
        try:
            return datetime.strptime(date_string, "%b %d, %Y").month
        except ValueError:
            return None

    df['Review Month'] = df['Subheader'].apply(extract_date)
    monthly_scores = df.groupby('Review Month')['Score'].mean()
    
    if not monthly_scores.empty:
        plt.figure(figsize=(12, 6))
        monthly_scores.plot(kind='bar')
        plt.title('Average Score by Month')
        plt.xlabel('Month')
        plt.ylabel('Average Score')
        plt.xticks(range(12), ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'])
    else:
        raise ValueError("No monthly score data available")

safe_plot(plot_score_by_month, 'score_by_month')

# 8. Simple sentiment analysis
def plot_sentiment_vs_score():
    def simple_sentiment(text):
        positive = len(re.findall(r'\b(good|great|excellent|amazing|fantastic|brilliant)\b', str(text), re.I))
        negative = len(re.findall(r'\b(bad|poor|terrible|awful|disappointing)\b', str(text), re.I))
        return positive - negative

    df['Sentiment'] = df['Content'].apply(simple_sentiment)
    plt.figure(figsize=(10, 6))
    sns.scatterplot(x='Sentiment', y='Score', data=df)
    plt.title('Review Sentiment vs Score')
    plt.xlabel('Sentiment (Positive - Negative word count)')
    plt.ylabel('Score')

safe_plot(plot_sentiment_vs_score, 'sentiment_vs_score')

# 9. Score distribution by year
def plot_score_by_year():
    df['Year'] = pd.to_datetime(df['Subheader'].str.extract('(\d{4})')[0], format='%Y')
    yearly_scores = df.groupby(df['Year'].dt.year)['Score'].mean().sort_index()
    plt.figure(figsize=(12, 6))
    yearly_scores.plot(kind='line', marker='o')
    plt.title('Average Score by Year')
    plt.xlabel('Year')
    plt.ylabel('Average Score')
    plt.xticks(rotation=45)

safe_plot(plot_score_by_year, 'score_by_year')

# 10. Word cloud of most common words in titles
def plot_title_word_cloud():
    from wordcloud import WordCloud
    title_text = ' '.join(df['Title'])
    wordcloud = WordCloud(width=800, height=400, background_color='white').generate(title_text)
    plt.figure(figsize=(10, 5))
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis('off')
    plt.title('Word Cloud of Game Titles')

safe_plot(plot_title_word_cloud, 'title_word_cloud')

# 11. Correlation heatmap
def plot_correlation_heatmap():
    numeric_df = df[['Score', 'Content Length', 'Subtitle Length', 'Subheader Word Count', 'Title Word Count', 'Sentiment']]
    corr = numeric_df.corr()
    plt.figure(figsize=(10, 8))
    sns.heatmap(corr, annot=True, cmap='coolwarm', vmin=-1, vmax=1, center=0)
    plt.title('Correlation Heatmap of Numeric Features')

safe_plot(plot_correlation_heatmap, 'correlation_heatmap')

# 12. Score distribution for games with specific words in title
def plot_score_by_title_keywords():
    keywords = ['Remastered', 'Edition', 'Deluxe', 'Ultimate', 'Definitive']
    data = []
    for keyword in keywords:
        scores = df[df['Title'].str.contains(keyword, case=False)]['Score']
        if not scores.empty:
            data.append(scores)
    
    if data:
        plt.figure(figsize=(12, 6))
        plt.boxplot(data, labels=keywords)
        plt.title('Score Distribution for Games with Specific Words in Title')
        plt.ylabel('Score')
    else:
        raise ValueError("No data available for the specified keywords")

safe_plot(plot_score_by_title_keywords, 'score_by_title_keywords')

# 13. Subheader length vs Score
def plot_subheader_length_vs_score():
    df['Subheader Length'] = df['Subheader'].str.len()
    plt.figure(figsize=(10, 6))
    sns.scatterplot(x='Subheader Length', y='Score', data=df)
    plt.title('Subheader Length vs Score')
    plt.xlabel('Subheader Length (characters)')
    plt.ylabel('Score')

safe_plot(plot_subheader_length_vs_score, 'subheader_length_vs_score')

# 14. Top reviewers by number of reviews
def plot_top_reviewers():
    reviewer_counts = df['Subtitle'].value_counts().head(10)
    plt.figure(figsize=(12, 6))
    reviewer_counts.plot(kind='bar')
    plt.title('Top 10 Reviewers by Number of Reviews')
    plt.xlabel('Reviewer')
    plt.ylabel('Number of Reviews')
    plt.xticks(rotation=45, ha='right')

safe_plot(plot_top_reviewers, 'top_reviewers')

# 15. Average score by reviewer (for top reviewers)
def plot_avg_score_by_reviewer():
    top_reviewers = df['Subtitle'].value_counts().head(10).index
    reviewer_avg_scores = df[df['Subtitle'].isin(top_reviewers)].groupby('Subtitle')['Score'].mean().sort_values(ascending=False)
    plt.figure(figsize=(12, 6))
    reviewer_avg_scores.plot(kind='bar')
    plt.title('Average Score by Top Reviewers')
    plt.xlabel('Reviewer')
    plt.ylabel('Average Score')
    plt.xticks(rotation=45, ha='right')

safe_plot(plot_avg_score_by_reviewer, 'avg_score_by_reviewer')

def plot_reviews_per_year():
    def extract_year(subheader):
        # Try to find the "Posted:" date first
        posted_match = re.search(r'Posted: (\w+ \d+, (\d{4}))', subheader)
        if posted_match:
            return int(posted_match.group(2))
        
        # If "Posted:" is not found, look for "Updated:" date
        updated_match = re.search(r'Updated: (\w+ \d+, (\d{4}))', subheader)
        if updated_match:
            return int(updated_match.group(2))
        
        # If neither is found, try to find any year
        year_match = re.search(r'\b(19|20)\d{2}\b', subheader)
        if year_match:
            return int(year_match.group())
        
        return None

    # Extract years from the Subheader column
    df['ReviewYear'] = df['Subheader'].apply(extract_year)

    # Count the number of reviews per year
    year_counts = df['ReviewYear'].value_counts().sort_index()

    # Plot
    plt.figure(figsize=(15, 8))
    year_counts.plot(kind='bar')
    plt.title('Number of Reviews per Year')
    plt.xlabel('Year')
    plt.ylabel('Number of Reviews')
    
    plt.xticks(range(len(year_counts)), year_counts.index, rotation=45)
    
    plt.tight_layout()

# Add this to your safe_plot calls
safe_plot(plot_reviews_per_year, 'reviews_per_year')


def plot_reviews_per_month():
    def extract_month(subheader):
        # Try to find the "Posted:" date first
        posted_match = re.search(r'Posted: (\w{3}) \d+, \d{4}', subheader)
        if posted_match:
            return posted_match.group(1)
        
        # If "Posted:" is not found, look for "Updated:" date
        updated_match = re.search(r'Updated: (\w{3}) \d+, \d{4}', subheader)
        if updated_match:
            return updated_match.group(1)
        
        return None

    # Extract months from the Subheader column
    df['ReviewMonth'] = df['Subheader'].apply(extract_month)

    # Count the number of reviews per month
    month_counts = df['ReviewMonth'].value_counts()

    # Create a dictionary to map month abbreviations to their numeric order
    month_order = {month: index for index, month in enumerate(month_abbr[1:], 1)}

    # Sort the month counts based on the numeric order
    month_counts_sorted = month_counts.sort_index(key=lambda x: x.map(month_order))

    # Plot
    plt.figure(figsize=(15, 8))
    month_counts_sorted.plot(kind='bar')
    plt.title('Number of Reviews per Month')
    plt.xlabel('Month')
    plt.ylabel('Number of Reviews')
    
    plt.xticks(rotation=45)
    plt.tight_layout()

safe_plot(plot_reviews_per_month, 'reviews_per_month')

print("Script execution completed.")

# PARA RODAR python generate_graphs.py