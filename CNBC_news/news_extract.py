import re
import pandas as pd
import requests
from bs4 import BeautifulSoup
from datetime import datetime


def get_current_date():
    now = datetime.now()
    return now.strftime("%Y%m%d")

def extract_sections(url):
    # Define empty dataframe with columns for title, date, and link 创建一个空的数据框
    df = pd.DataFrame(columns=['Section', 'link'])

    # Send a request to the URL and get the HTML content 发送请求并获取 HTML 内容
    response = requests.get(url)
    html_content = response.content

    # Parse the HTML content using BeautifulSoup 解析 HTML 内容
    soup = BeautifulSoup(html_content, "html.parser")

    # Find the list of articles in the section 找到文章列表
    section_list = soup.find_all("a", {"class": "nav-menu-button"})

    # Loop through the list of articles and extract the title, date, and link of each article 循环遍历文章列表，提取标题、日期和链接
    for i, section in enumerate(section_list):
        # Extract the title of the article 提取文章标题
        title = section.text.strip()

        # Extract the href of the article 提取文章链接
        href = section.get("href")

        # print(f'Section: {title}, link: {href}')
        data = {'Section': title, 'link': href}
        df = pd.concat([df, pd.DataFrame(data, index=pd.RangeIndex(len(data['Section'])))])

    # 去重输出
    df.drop_duplicates(inplace=True)
    return(df)



def extract_cnbc_articles(url,section):
    # Define empty dataframe with columns for title, date, and link 创建一个空的数据框
    df = pd.DataFrame(columns=['title', 'date', 'link', 'section'])

    # Send a request to the URL and get the HTML content 发送请求并获取 HTML 内容
    response = requests.get(url)
    html_content = response.content

    # Parse the HTML content using BeautifulSoup 解析 HTML 内容
    soup = BeautifulSoup(html_content, "html.parser")

    # Find the list of articles in the section 找到文章列表
    article_list = soup.find_all("div", {"class": "Card-titleContainer"})

    # Loop through the list of articles and extract the title, date, and link of each article 循环遍历文章列表，提取标题、日期和链接
    for i, article in enumerate(article_list):
        # Extract the title of the article 提取文章标题
        title = article.find("a").text.strip()

        # Extract the href of the article 提取文章链接
        href = article.find("a")["href"]

        # Extract the date of the article from the href 提取文章日期
        date_pattern = r'\d{4}/\d{2}/\d{2}'  # matches "YYYY/MM/DD"
        match = re.search(date_pattern, href)

        if match:
            date = match.group()
        else:
            date = 'NA'

        # Print the title, date and href of the article 打印文章标题、日期和链接
        print(f"Article {i+1}: {title}; Date: {date}; Link: {href}")

        # Add the title, date, and link to the dataframe 将数据添加到数据框中
        data = {'title': title, 'date': date, 'link': href, 'section': section}
        df = pd.concat([df, pd.DataFrame(data, index=pd.RangeIndex(len(data['title'])))])
        df.drop_duplicates(inplace=True)

    # Get the date for the output file name
    # max_date = max(df.iloc[:, 1])
    # date = datetime.strptime(max_date, '%Y/%m/%d').strftime('%Y%m%d')
    date = ''
    section = url.split("/")[-2]

    # Save the dataframe
    df = df.sort_values(by='date', ascending=False)
    return(df)
    # df.to_csv(f'{section}_{date}.csv', index=False)
    # print(f'News file: "{section}_{date}.csv" is output.')


###########################################################
# 程序的主要功能是从 CNBC 的技术新闻页面提取文章的标题、日期和链接，并将这些信息保存到一个 CSV 文件中
# Invoke function 调用函数
if __name__ == '__main__':
    today = get_current_date()
    url = "https://www.cnbc.com/"
    df = extract_sections(url)
    num = 0
    with pd.ExcelWriter(f'output_{today}.xlsx') as writer:
        # read first 5 sections in CNBC
        for i in range(5):
            section = df.iloc[i,0]
            url_section = url[:-1] + df.iloc[i,1]

            df_section = extract_cnbc_articles(url_section,section)
            df_section.to_excel(writer, sheet_name=section, index=False)
            num = num + df_section.shape[0]
    print(f'File "output_{today}.xlsx" is output, with total {num} news being crawled.')
