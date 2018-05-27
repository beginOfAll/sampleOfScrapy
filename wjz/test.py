import requests
from bs4 import BeautifulSoup
import json

result = []

req = requests.get('https://movie.douban.com/chart')
with open('chart.html', 'w', encoding='utf-8') as f:
    f.write(req.text)
soup = BeautifulSoup(req.text, 'html.parser')
div = soup.find_all('div', class_='types')
print(len(div))
for child in div[0].children:
    if child.name == 'span':
        a = child.a
        note = dict()
        note['category'] = a.text
        note['url'] = 'https://movie.douban.com' + a['href']
        result.append(note)
print(result)

with open('chart.json', 'w', encoding='utf-8') as f:
    json.dump(result, f, ensure_ascii=False)
