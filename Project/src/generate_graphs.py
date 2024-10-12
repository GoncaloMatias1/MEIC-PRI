import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

data_path = 'webscrapper_out/ign.csv' 

df = pd.read_csv(data_path)

print("Primeiras linhas do dataset:")
print(df.head())

df['Title Length'] = df['Title'].str.len()
df['Subtitle Length'] = df['Subtitle'].str.len()
df['Content Length'] = df['Content'].str.len()

# Gráfico 1: Distribuição dos Scores
plt.figure(figsize=(10, 6))
sns.histplot(df['Score'], bins=20, kde=True)
plt.title('Distribution of Game Scores')
plt.xlabel('Score')
plt.ylabel('Frequency')
plt.savefig('../docs/score_distribution.png')  
plt.show()

# Gráfico 2: Distribuição do Tamanho dos Títulos
plt.figure(figsize=(10, 6))
sns.histplot(df['Title Length'], bins=20, kde=True)
plt.title('Distribution of Title Lengths')
plt.xlabel('Length of Title (characters)')
plt.ylabel('Frequency')
plt.savefig('../docs/title_length_distribution.png')  
plt.show()

# Gráfico 3: Distribuição do Tamanho das Legendas
plt.figure(figsize=(10, 6))
sns.histplot(df['Subtitle Length'], bins=20, kde=True)
plt.title('Distribution of Subtitle Lengths')
plt.xlabel('Length of Subtitle (characters)')
plt.ylabel('Frequency')
plt.savefig('../docs/subtitle_length_distribution.png')  
plt.show()

# Gráfico 4: Distribuição do Tamanho do Conteúdo
plt.figure(figsize=(10, 6))
sns.histplot(df['Content Length'], bins=20, kde=True)
plt.title('Distribution of Content Lengths')
plt.xlabel('Length of Content (characters)')
plt.ylabel('Frequency')
plt.savefig('../docs/content_length_distribution.png') 
plt.show()


# PARA RODAR python generate_graphs.py