import requests

headers = {
    'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.146 Safari/537.36',
    # 'Host': 'www.baidu.com'
}

req = requests.get('https://www.baidu.com/s?wd=%E5%BF%AB%E9%80%92%2B%E5%91%83%E6%94%B6%E4%BB%B6%E4%BA%BA',
                   # verify="/home/wjz/Builtin Object Token_GlobalSign Root CA",
                   # verify=True,
                   headers=headers
                   )
with open('charts.html', 'w', encoding='utf-8') as f:
    f.write(req.text)
