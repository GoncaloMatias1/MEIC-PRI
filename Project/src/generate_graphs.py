import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import re
from datetime import datetime
from collections import Counter
from calendar import month_abbr
from wordcloud import WordCloud

data_path = 'webscrapper_out/ign.csv'
df = pd.read_csv(data_path)

print(f"Successfully read CSV file from {data_path}")
print(f"Number of rows: {len(df)}")
print(f"Number of columns: {len(df.columns)}")
print("Columns in the DataFrame:")
print(df.columns.tolist())

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


# 2. Content Length vs Score
def plot_content_length_vs_score():
    df['Content Length'] = df['Content'].str.len()
    plt.figure(figsize=(10, 6))
    sns.scatterplot(x='Content Length', y='Score', data=df)
    plt.title('Review Content Length vs Score')
    plt.xlabel('Content Length (characters)')
    plt.ylabel('Score')

safe_plot(plot_content_length_vs_score, 'content_length_vs_score')


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

def extract_original_date(subheader):
    # Try to find the "Posted:" date first
    posted_match = re.search(r'Posted: (\w+ \d+, \d{4})', subheader)
    if posted_match:
        return datetime.strptime(posted_match.group(1), '%b %d, %Y')
    
    # If "Posted:" is not found, look for any date
    date_match = re.search(r'(\w+ \d+, \d{4})', subheader)
    if date_match:
        return datetime.strptime(date_match.group(1), '%b %d, %Y')
    
    return None

def plot_avg_score_per_year():
    # Extract original dates from the Subheader column
    df['ReviewDate'] = df['Subheader'].apply(extract_original_date)
    df['ReviewYear'] = df['ReviewDate'].dt.year

    # Calculate average score per year
    yearly_avg_scores = df.groupby('ReviewYear')['Score'].mean().sort_index()

    # Plot
    plt.figure(figsize=(15, 8))
    yearly_avg_scores.plot(kind='line', marker='o')
    plt.title('Average Score per Year')
    plt.xlabel('Year')
    plt.ylabel('Average Score')
    
    plt.xticks(rotation=45)
    plt.grid(True, which='both', linestyle='--', linewidth=0.5)
    plt.tight_layout()

safe_plot(plot_avg_score_per_year, 'avg_score_per_year')


def extract_reviewer(subheader):
    # Try to find the reviewer name
    reviewer_match = re.search(r'By ([\w\s]+) Updated:', subheader)
    if reviewer_match:
        return reviewer_match.group(1).strip()
    return "Unknown"

def plot_top_reviewers():
    # Extract reviewer names
    df['Reviewer'] = df['Subheader'].apply(extract_reviewer)
    
    # Count reviews per reviewer
    reviewer_counts = df['Reviewer'].value_counts()
    
    # Get top 20 reviewers
    top_20_reviewers = reviewer_counts.head(20)
    
    # Plot
    plt.figure(figsize=(15, 10))
    bars = plt.bar(top_20_reviewers.index, top_20_reviewers.values)
    plt.title('Top 20 Reviewers by Number of Reviews')
    plt.xlabel('Reviewer')
    plt.ylabel('Number of Reviews')
    plt.xticks(rotation=90)
    
    for bar in bars:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height,
                 f'{height}',
                 ha='center', va='bottom')
    
    plt.tight_layout()

safe_plot(plot_top_reviewers, 'top_20_reviewers')

def plot_avg_score_per_top_reviewer():
    df['Reviewer'] = df['Subheader'].apply(extract_reviewer)
    
    # Calculate average score per reviewer
    avg_scores = df.groupby('Reviewer')['Score'].agg(['mean', 'count'])
    avg_scores = avg_scores[avg_scores['count'] >= 10]  
    avg_scores = avg_scores.sort_values('count', ascending=False).head(20)
    
    # Plot
    plt.figure(figsize=(15, 10))
    bars = plt.bar(avg_scores.index, avg_scores['mean'])
    plt.title('Average Score by Top 20 Reviewers (min. 10 reviews)')
    plt.xlabel('Reviewer')
    plt.ylabel('Average Score')
    plt.xticks(rotation=90)
    
    for bar in bars:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height,
                 f'{height:.2f}',
                 ha='center', va='bottom')
    
    plt.tight_layout()

safe_plot(plot_avg_score_per_top_reviewer, 'avg_score_per_top_reviewer')


def plot_avg_score_top_20_reviewers():
    df['Reviewer'] = df['Subheader'].apply(extract_reviewer)
    
    top_20_reviewers = df['Reviewer'].value_counts().nlargest(20).index

    # Calculate average score for top 20 reviewers
    avg_scores = df[df['Reviewer'].isin(top_20_reviewers)].groupby('Reviewer')['Score'].agg(['mean', 'count']).sort_values('count', ascending=False)

    # Plot
    plt.figure(figsize=(20, 10))  
    bars = plt.bar(avg_scores.index, avg_scores['mean'])
    plt.title('Average Score by Top 20 Reviewers')
    plt.xlabel('Reviewer')
    plt.ylabel('Average Score')
    plt.ylim(0, 10)  
    
    plt.xticks(rotation=45, ha='right')
    
    # Add value labels on top of each bar
    for bar in bars:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height,
                 f'{height:.2f}',
                 ha='center', va='bottom')
    
    # Add number of reviews as text below the x-axis
    for i, (reviewer, data) in enumerate(avg_scores.iterrows()):
        plt.text(i, -0.3, f"n={data['count']}", ha='center', va='top', rotation=45, transform=plt.gca().get_xaxis_transform())
    
    plt.tight_layout()


safe_plot(plot_avg_score_top_20_reviewers, 'avg_score_top_20_reviewers_improved')

def plot_grouped_score_distribution():
    bins = [0, 2, 4, 6, 8, 10]
    labels = ['1-2', '3-4', '5-6', '7-8', '9-10']

    # Agrupar os dados e contar as reviews em cada intervalo
    df['Score Group'] = pd.cut(df['Score'], bins=bins, labels=labels)
    score_group_counts = df['Score Group'].value_counts().sort_index()

    # Plot
    plt.figure(figsize=(12, 6))
    bars = plt.bar(score_group_counts.index, score_group_counts.values)  
    plt.title('Grouped Distribution of Review Scores')
    plt.xlabel('Score Groups')
    plt.ylabel('Number of Reviews')

    # Adicionar etiquetas de valor no topo de cada barra
    for bar in bars:
        height = bar.get_height()
        plt.annotate(f'{int(height)}',
                     xy=(bar.get_x() + bar.get_width() / 2, height),
                     xytext=(0, 3),  
                     textcoords="offset points",
                     ha='center', va='bottom')

    plt.tight_layout()

safe_plot(plot_grouped_score_distribution, 'grouped_score_distribution')

def plot_title_word_cloud(df):
    title_text = ' '.join(df['Title'])
    # Clean the text
    title_text = re.sub(r'[^\w\s]', '', title_text)  # Remove punctuation
    title_text = title_text.lower()  # Convert to lowercase
    # Create and generate a word cloud image
    wordcloud = WordCloud(width=800, height=400, background_color='white').generate(title_text)
    # Display the generated image
    plt.figure(figsize=(10, 5))
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis('off')
    plt.title('Word Cloud of Game Titles')

def plot_subtitle_word_cloud(df):
    subtitle_text = ' '.join(df['Subtitle'].dropna().astype(str))
    # Clean the text
    subtitle_text = re.sub(r'[^\w\s]', '', subtitle_text)  # Remove punctuation
    subtitle_text = subtitle_text.lower()  # Convert to lowercase
    # Create and generate a word cloud image
    wordcloud = WordCloud(width=800, height=400, background_color='white').generate(subtitle_text)
    # Display the generated image
    plt.figure(figsize=(10, 5))
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis('off')
    plt.title('Word Cloud of Game Subtitles')

def plot_content_word_cloud(df):
    content_text = ' '.join(df['Content'].dropna().astype(str))
    # Clean the text
    content_text = re.sub(r'[^\w\s]', '', content_text)  # Remove punctuation
    content_text = content_text.lower()  # Convert to lowercase
    # Create and generate a word cloud image
    wordcloud = WordCloud(width=800, height=400, background_color='white', max_words=200).generate(content_text)
    # Display the generated image
    plt.figure(figsize=(10, 5))
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis('off')
    plt.title('Word Cloud of Game Reviews Content')

safe_plot(lambda: plot_title_word_cloud(df), 'title_word_cloud')
safe_plot(lambda: plot_subtitle_word_cloud(df), 'subtitle_word_cloud')
safe_plot(lambda: plot_content_word_cloud(df), 'content_word_cloud')

print("Script execution completed.")

# PARA RODAR python generate_graphs.py