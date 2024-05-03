import requests
from bs4 import BeautifulSoup
import re
import pandas as pd
import jieba
import jieba.analyse

import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties
from community import community_louvain
import matplotlib as mpl
from matplotlib.font_manager import fontManager

# 爬取電影評論
class MovieReviewScraper:
    def __init__(self, base_url = 'https://news.agentm.tw/category/電影影評/'):
        self.base_url = base_url
        self.content_urls = []
        self.movie_names = []
        self.data = []

    @staticmethod # @staticmethod 的意義就是可以直接調用 def函數，不用創建實體

    def extract_movie_name(title):
        pattern = r'《(.*?)》'
        movie_names = re.findall(pattern, title)
        return movie_names[0] if movie_names else None

    def fetch_review_links(self):
        response = requests.get(self.base_url)
        if response.ok:
            soup = BeautifulSoup(response.text, 'html.parser')
            h3_tags = soup.find_all('h3', class_='ec-title')
            for h3 in h3_tags:
                a_tag = h3.find('a')
                if a_tag:
                    link = a_tag.get('href', '')
                    title = a_tag.get('title', '')
                    movie_name = self.extract_movie_name(title)
                    if link and movie_name:
                        self.content_urls.append(link)
                        self.movie_names.append(movie_name)

    def scrape_review_contents(self):
        for url in self.content_urls:
            response = requests.get(url)
            if response.ok:
                soup = BeautifulSoup(response.text, 'html.parser')
                # 假設評論內容被包含在某個HTML元素中，這裡需要根據實際情況調整
                content = soup.get_text()
                
                # 使用strip()移除首尾的空白字符（包括\n）
                cleaned_content = content.strip()
                # 進一步去除所有換行符
                cleaned_content = cleaned_content.replace('\n', '')
                # Get rid off English and numbers in the content
                cleaned_content = re.sub(r'[A-Za-z0-9]', '', cleaned_content)
                self.data.append({
                    'url': url,
                    'content': cleaned_content,
                    'movie_name': self.extract_movie_name(soup.title.string if soup.title else "")
                })


    def extract_keywords(self, text):
        return jieba.analyse.extract_tags(text, topK=10)

    def process_reviews(self):
        df = pd.DataFrame(self.data)
        df['keywords'] = df['content'].apply(self.extract_keywords)
        return df

## Example of using the class
# scraper = MovieReviewScraper('https://news.agentm.tw/category/電影影評/')
# scraper.fetch_review_links()
# scraper.scrape_review_contents()
# df_reviews = scraper.process_reviews()
# print(df_reviews.head())



import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties
from community import community_louvain
import matplotlib as mpl


# 繪製網絡關係圖
class MovieReviewNetwork:
    def __init__(self):
        self.graph = nx.Graph()
        self.setup_plot_style()

    def add_reviews_to_graph(self, df):
        """ 將電影名稱和關鍵字加入到圖形中 """
        for index, row in df.iterrows():
            movie_name = row['movie_name']
            keywords = row['keywords']
            
            self.graph.add_node(movie_name, type='author')  # Match original node type
            
            for keyword in keywords:
                self.graph.add_node(keyword, type='keyword')
                self.graph.add_edge(movie_name, keyword)

    def setup_plot_style(self):
        """ 設定繪圖風格和字型 """
        font_path = 'TaipeiSansTCBeta-Regular.ttf'
        fontManager.addfont(font_path)
        mpl.rc('font', family='Taipei Sans TC Beta')
        plt.style.use('default')  # Use default style to match the original style

    def draw_graph(self):
        """ 繪製網絡圖，包括社群顏色、節點大小和透明度設定 """
        pos = nx.spring_layout(self.graph, k=0.2, iterations=80)
        partition = community_louvain.best_partition(self.graph)
        cmap = plt.cm.jet  # Change to match original color map
        community_colors = max(partition.values()) + 1
        colors = [cmap(partition[node] / community_colors) for node in self.graph]
        colors_with_alpha = [(r, g, b, 0.3) for r, g, b, _ in colors]
        node_sizes = [200 * self.graph.degree(node) for node in self.graph]

        plt.figure(figsize=(30, 30))
        nx.draw_networkx_edges(self.graph, pos, alpha=0.5)
        nx.draw_networkx_nodes(self.graph, pos, node_color=colors_with_alpha, node_size=node_sizes, cmap=cmap)
        nx.draw_networkx_labels(self.graph, pos, font_size=20, font_family='Taipei Sans TC Beta')
        
        plt.axis('off')
        plt.show()

# # 使用範例
# # 假設df是包含movie_name和keywords的DataFrame
# network = MovieReviewNetwork()
# network.add_reviews_to_graph(df)
# network.draw_graph()
