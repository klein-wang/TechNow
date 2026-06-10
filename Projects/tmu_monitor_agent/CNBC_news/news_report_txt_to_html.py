import os
from datetime import datetime


def get_current_date():
    now = datetime.now()
    return now.strftime("%Y%m%d")

today = get_current_date()

script_dir = os.path.dirname(os.path.abspath(__file__))
input_dir = os.path.join(script_dir, f"news_summary_{today}.txt") 
output_dir = os.path.join(script_dir, f'report_{today}.html') 

html_content = ''

with open(input_dir) as f:
    lines = f.readlines()

current_company = ''
html_content += f'<div>'

for line in lines:

    line = line.strip()

    if line.startswith('Company'):
        start, name = line.split(': ')
        company = name.strip()

        if company != current_company:
            html_content += '<div class="company">'
            html_content += f'<h2>{company}</h2>'
            html_content += '<div class="articles">'
            current_company = company

    elif line.startswith('--'):

        if line.startswith('--20'):
            date, title = line.split(': ', maxsplit=1)
            title = title.strip()

        else:
            start, link = line.split(': ', maxsplit=1)
            link = link[:-1]

            # html_content += f'<h4>{date}</h4>'
            html_content += f'<h3>{title}</h3>'
            html_content += f'<a class="link" style="text-decoration: underline;" href="{link}"> *article link* </a>'

    elif line.startswith('____'):
        html_content += '</div>'
        html_content += "<div style='height: 20px;'></div>"



html = """
  <!DOCTYPE html>
  <html>
  <head>
    <style>
    
    header {
      background: #d6d6d6;
      color: black;
      padding: 20px;  
      max-width: 1000px;  
      margin: 0 auto;
      text-align: center;
    }
    
    body {
      font-family: Arial, sans-serif;
      max-width: 1000px;
      margin: 0 auto;
    }
    
    h1 {
      text-align: center;
    }
    
    .company {
      background: white;
      margin-top: 30px;
      <!-- padding: 15px; 依次向右偏移 -->
      border: 1px solid #ddd;
      border-radius: 10px;
    }
    
    .articles {
      padding-left: 15px; 
    }
    
    h2 {
      color: black;
    }
    
    h3, h4 {
      color: #457b1a;
      margin: 10px 0;
    }
    
    h3 {
      text-align: center;
    }
    
    p {
      color: black;
      margin: 10px 0;
    }
    
    a:link {
       color: black;
       background-color: transparent;
       text-decoration: none;
       text-align:center;
    }
    a:visited {
       color: deepskyblue;
       background-color: transparent;
       text-decoration: none;
    }
    a:active {
       color: greenyellow;
       background-color: transparent;
    }
    
    .link {
      position: relative;
      text-decoration: underline;
      buttom: 5px;
      left: 450px;
    }
    
    
    </style>
  </head>
  
  <header>
  <h1>Financial News Report</h1>
  <p>{today}</p>
  </header>
  
  <body>
    {html_content}
  </body>
  </html>
"""

with open(output_dir, 'w') as f:

  html = html.replace('{html_content}', html_content)
  html = html.replace('{today}', today)


  f.write(html)


print("HTML report generated!")