# loading packages
import os
import re
import pandas as pd
from datetime import datetime
import news_extract as cnbc
import matplotlib.pyplot as plt
import spacy
# python3 -m spacy download en_core_web_trf
nlp = spacy.load('en_core_web_trf') # Loading Spacy's English model
# try 'en_core_web_md' or 'en_core_web_lg' for higher accuracy


# extract news with article url
def extract_news(url):

    df_section = cnbc.extract_sections(url)
    
    if df_section.empty:
        print("Warning: No sections found in the page.")
        return pd.DataFrame()
    
    dfs = []
    for i in range(5): # set section range to first 5 categories
        section = df_section.iloc[i, 0]
        url_section = url[:-1] + df_section.iloc[i, 1]

        df = cnbc.extract_cnbc_articles(url_section, section)
        dfs.append(df[df['date'] != 'NA'])
    df = pd.concat(dfs) # df.date.drop_duplicates() -- check unique dates

    return (df)
    print(f'News are extracted up to {max(df.date)}, with total {len(df)} news being crawled.')

# extract company name from news title
def extract_company_names(text):
    doc = nlp(text)
    return [ent.text for ent in doc.ents if ent.label_ == 'ORG']


# group the news by company names
def group_by_company_names(df):
    df['company_names'] = df['title'].apply(extract_company_names)
    # Explode 'company_names' column to create a new row for each company in the list
    df_exploded = df.explode('company_names')

    # Group by 'company_names' and join the titles, dates, links, and sections for each company
    grouped = df_exploded.groupby('company_names').agg({
        'title': ', '.join,
        'date': list,
        'link': list,
        'section': list
    }).reset_index()

    # Drop rows where 'company_names' is None or an empty string
    grouped = grouped[grouped['company_names'].notna() & (grouped['company_names'] != '')]

    return(grouped)
        
# output news summary by company
def output_report(df):
    today = datetime.now().strftime('%Y%m%d')
    script_dir = os.path.dirname(os.path.abspath(__file__))
    output_dir = os.path.join(script_dir, f"news_summary_{today}.txt") 
    with open(output_dir, 'w') as f:
        # Iterate over each row of the dataframe
        for index, row in df.iterrows():
            # Get the company name
            company_name = row['company_names']
            title = row['title']
            date = row['date']
            link = row['link']

            # Print out the news summary by company
            f.write(f"Company: {company_name}\n")
            # f.write("--Summary of Recent News:\n")

            title_list = []
            for i in range(len(date)):
                title_i = title.split(';')[i]
                if title_i[0] == ',':
                   title_i = title_i[2:] # remove ', ' for >=2 entries
                date_i = date[i]
                link_i = link[i]

                if title_i not in title_list:
                    f.write(f"--{date_i}: {title_i};\n")
                    f.write(f"--Link: {link_i};\n")
                    title_list.append(title_i)

            f.write("____" * 20 + "\n" * 2)  # Visually separate news



###########################################################
# 程序的主要功能是从 CNBC 的技术新闻页面提取文章的标题、日期和链接，并将这些信息提取，根据公司和新闻日期来进行整理
# Invoke function 调用函数
if __name__ == '__main__':
    today = cnbc.get_current_date()
    url = "https://www.cnbc.com/"
    df_news = extract_news(url)
    print("success")
    df_grouped = group_by_company_names(df_news)
    print("success")
    # output news summary report
    output_report(df_grouped)
