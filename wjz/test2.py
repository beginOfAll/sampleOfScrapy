from selenium import webdriver
import time

browser = webdriver.PhantomJS()
# browser.get('http://www.baidu.com')
print(time.time())
browser.get('https://item.jd.com/4709296.html')
print(time.time())
src = browser.page_source
print(src.find('9999'))
