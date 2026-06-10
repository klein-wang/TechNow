import re
import pandas as pd
from datetime import datetime
import news_extract as cnbc
import matplotlib.pyplot as plt
from wordcloud import WordCloud
import stopwords


def extract_news(url):

    df_section = cnbc.extract_sections(url)
    dfs = []
    for i in range(5): # set section range to first 5 categories
        section = df_section.iloc[i, 0]
        url_section = url[:-1] + df_section.iloc[i, 1]

        df = cnbc.extract_cnbc_articles(url_section, section)
        dfs.append(df[df['date'] != 'NA'])
    df = pd.concat(dfs) # df.date.drop_duplicates() -- check unique dates

    return (df)
    print(f'News are extracted up to {max(df.date)}, with total {len(df)} news being crawled.')



def plot_wordcloud(date,df_news,theme,background_color,word_nums):

    # Concatenate all text after removing stopwords from text
    all_text = ' '.join(df_news['title'])
    stops = stopwords.get_stopwords("english")
    all_text_cleaned = ' '.join([word for word in all_text.split() if word not in stops])

    # Generate the word cloud
    wordcloud = WordCloud(colormap=theme,background_color=background_color,
                          width=800, height=1200,
                          random_state=30, max_font_size=120, max_words = word_nums
                          ).generate(all_text_cleaned)


    # Plot the WordCloud image
    plt.figure(figsize=(10, 8), facecolor=None)
    plt.imshow(wordcloud)
    plt.axis("off")
    plt.tight_layout(pad=0)

    # Save the image
    wordcloud.to_file(f'{date}_wordcloud_{theme}_{background_color}.png')

    # Display the image
    plt.show()



###########################################################
# 程序的主要功能是从 CNBC 的技术新闻页面提取文章的标题、日期和链接，并将这些信息提取到一个 wordcloud 文件中
# Invoke function 调用函数
if __name__ == '__main__':
    today = cnbc.get_current_date()
    url = "https://www.cnbc.com/"
    df_news = extract_news(url)

    # plot wordcloud
    themes = ['viridis','plasma','magma','inferno','cividis']
    colors = ['black','white','Blues', 'Greens', 'Oranges', 'Reds',
                      'YlOrBr', 'YlOrRd', 'OrRd', 'PuRd', 'RdPu', 'BuPu',
                      'GnBu', 'PuBu', 'YlGnBu', 'PuBuGn', 'BuGn', 'YlGn']
    plot_wordcloud(today,df_news,theme=themes[0],background_color=colors[1],word_nums = 200)
