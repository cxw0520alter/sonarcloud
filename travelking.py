#!/usr/bin/env python
# coding: utf-8

# In[3]:


import requests as rq
from bs4 import BeautifulSoup as bs
import re
import requests
import time


# In[4]:


def gethtml(rooturl, encoding="utf-8"):
    # 預設解碼方式utf-8
    response = rq.get(rooturl)
    response.encoding = encoding
    html = response.text
    return html  # 返回連結的html內容


# In[5]:


def getherf(html):
    # 使用BeautifulSoup函式解析傳入的html
    soup = bs(html, features="lxml")
    allnode_of_a = soup.find_all("a")
    result = [_.get("href") for _ in allnode_of_a]
    #if "/tourguide/scenery" in result:
    #print(result)
    return result


# In[6]:


def filterurl(result):
    # result引數：get到的所有a標籤內herf的內容
    # 對列表中每個元素進行篩選
    urlptn = r"/tourguide/scenery(.+)"  # 匹配模式: 所有http://開頭的連結
    urls = [re.match(urlptn, str(_)) for _ in result]  # 正則篩選
    # print(urls)
    while None in urls:
        urls.remove(None)  # 移除表中空元素
    urls = [_.group() for _ in urls]  # group方法獲得re.match()返回值中的字元
    # print(urls)
    return urls


# In[7]:


def pxpy(result):
    # result引數：get到的所有a標籤內herf的內容
    # 對列表中每個元素進行篩選
    urlptn = r"https://www.google.com.tw/maps/search/(.+)"  # 匹配模式: 所有http://開頭的連結
    urls = [re.match(urlptn, str(_)) for _ in result]  # 正則篩選
    # print(urls)
    while None in urls:
        urls.remove(None)  # 移除表中空元素
    urls = [_.group() for _ in urls]  # group方法獲得re.match()返回值中的字元
    # print(urls)
    return urls


# In[8]:


html = gethtml("https://www.travelking.com.tw/tourguide/taiwan/taichung-city/")
result = getherf(html)
urls = filterurl(result)
ur = ["https://www.travelking.com.tw" + url for url in urls]
print(ur)


# In[28]:


my_dict = {}
i=0
for url in ur:
    flag=1
    print(url)
    #time.sleep(3)
    html = gethtml(url)
    result = getherf(html)
    urls = pxpy(result)
    print(urls)
    if len(urls) == 0:
        flag=0
    #print(flag)
    if flag==1 :   
        coord_string = urls[0].split('/')[-1]
        latitude, longitude = coord_string.split(',')
        #print(latitude, longitude)
    else :
        latitude = None
        longitude = None
    response = requests.get(url)
# 使用 BeautifulSoup 解析 HTML
    soup = bs(response.text, "html.parser")
# 查找包含評分信息的 HTML 元素
    rating_element  = soup.find_all("h1",{"class":"h1"})
    text = soup.find('span', {'property': 'dc:title'}).get_text()
    pointype = soup.find('span', {'property': 'rdfs:label'}).strong.get_text()
    hotvalue = soup.find('span', {'class': 'hotvalue'}).b.get_text()
    try:
        address = soup.find('span', {'property': 'vcard:street-address'}).get_text()
    except AttributeError:
        address = None
    try:
        description = soup.find('div', {'class': 'point_list'}).p.get_text()
    except AttributeError:
        description = None
    my_dict[i] = {"地点": text, "类型": pointype, "人气": hotvalue, "地址": address, "描述": description, "Px": latitude, "Py": longitude}
    print(my_dict[i])
    i=i+1
    


# In[ ]:


import csv


# In[11]:


#travelking 資料儲存
with open('taichung.csv', 'w', newline='', encoding='utf-8') as csvfile:
    fieldnames = ['地点', '类型', '人气', '地址', '描述', 'Px', 'Py']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    for key, value in my_dict.items():
        writer.writerow(value)


# In[27]:


#根據travelking名稱爬取google評分
from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementNotInteractableException
from typing import Union
from urllib import parse

# Fully matched: 直接搜尋到目標頁面，可以看得到Business data。
# Highly matched: 搜尋頁面會列出多個搜尋結果，我們預設抓第一個結果。
# Low matched: 搜尋頁面顯示[部分符合的結果]，同樣會列出搜尋結果，但非常少(可能只有一筆)。
# No matched: 找不到任何結果。

# Definition of constants
BASE_URL = "https://www.google.com.tw/maps/search/"
PAGE_BRANCH_SELECTORS = {
    # get_attribute("href")
    "search_highly_matched": "div[aria-label$=搜尋結果][role=\"feed\"] a:nth-child(1)",
    # get_attribute("href")
    "search_low_matched": "div[aria-label$=搜尋結果][role=\"feed\"] a:nth-child(1)"
}
_RELATIVE_INFO_TARGET_BLOCK = "div[class=\"m6QErb \"][role=\"region\"][aria-label$=\"相關資訊\"]"
TARGET_ELEMENT_SELECTORS = {
    "name": "div[role=\"main\"] h1[class=\"DUwDvf fontHeadlineLarge\"]",
    "rating": "div[role=\"main\"] div[class=\"F7nice \"] span:nth-child(1) span:nth-child(1)",
    "total_reviews": "div[role=\"main\"] div[class=\"F7nice \"] span:nth-child(1) span[aria-label]:nth-child(1)",
    "place_type": "button[class=\"DkEaL \"]",
    # get_attribute("aria-label")
    "address": f"{_RELATIVE_INFO_TARGET_BLOCK} button[class=\"CsEnBe\"][aria-label^=\"地址\"][data-item-id=\"address\"]",
    # get_attribute("aria-label")
    "website": f"{_RELATIVE_INFO_TARGET_BLOCK} a[class=\"CsEnBe\"][aria-label^=\"網站\"][data-item-id=\"authority\"]",
    # get_attribute("aria-label")
    "phone_number": f"{_RELATIVE_INFO_TARGET_BLOCK} button[class=\"CsEnBe\"][aria-label^=\"電話號碼\"]",
    # used to find the drop-down button, we need to click on it
    "opening_hours": "div[class=\"OMl5r hH0dDd jBYmhd\"][data-hide-tooltip-on-mouse-move=\"true\"][aria-expanded=\"false\"][role=\"button\"]"
}
# total 7 elements
OPENING_HOURS_ELEMENT_ITEMS_SELECTOR = "table[class^=\"eK4R0e\"] tbody tr[class=\"y0skZc\"]"
OPENING_HOURS_ITEM_WEEK_ELEMENT_SELECTOR = "table[class^=\"eK4R0e\"] tbody tr[class=\"y0skZc\"] td[class^=\"ylH6lf \"] div"
OPENING_HOURS_ITEM_DURATION_ELEMENT_SELECTOR = "table[class^=\"eK4R0e\"] tbody tr[class=\"y0skZc\"] td[class=\"mxowUb\"] li[class=\"G8aQO\"]"

BUSINESS_DATA_FIELDS = ("name", "rating", "total_reviews", "place_type", "address", "website", "phone_number", "opening_hours")


class CustomCondition:
    class get_business_elements:
        def __init__(self, data: dict):
            self.data = data

        def __call__(self, driver) -> bool:
            """
            Find elements to update data dictionary
            """
            for field in BUSINESS_DATA_FIELDS[:4]:
                if self.data[field] is None:
                    try:
                        ele = driver.find_element(By.CSS_SELECTOR, TARGET_ELEMENT_SELECTORS[field])
                        self.data[field] = ele.text
                    except NoSuchElementException:
                        pass
            for field in BUSINESS_DATA_FIELDS[4:4+3]:
                if self.data[field] is None:
                    try:
                        ele = driver.find_element(By.CSS_SELECTOR, TARGET_ELEMENT_SELECTORS[field])
                        self.data[field] = ele.get_attribute("aria-label")
                    except NoSuchElementException:
                        pass

            # handle opening hours
            # 在此之前必須操控selenium點開營業時間的標籤，否則抓不到資料
            try:
                drop_down_ele = driver.find_element(By.CSS_SELECTOR, TARGET_ELEMENT_SELECTORS["opening_hours"])
                # 找到之後滾動頁面到該元素位置，確認它可以被selenium看到
                action = ActionChains(driver)
                action.move_to_element(drop_down_ele).perform()
                drop_down_ele.click()
            except NoSuchElementException:
                pass
            except ElementNotInteractableException:
                pass
            # 抓opening_hours資料
            try:
                ele_list = driver.find_elements(By.CSS_SELECTOR, OPENING_HOURS_ELEMENT_ITEMS_SELECTOR)
                for ele in ele_list:
                    week = ele.find_element(By.CSS_SELECTOR, OPENING_HOURS_ITEM_WEEK_ELEMENT_SELECTOR).text
                    durations = ele.find_elements(By.CSS_SELECTOR, OPENING_HOURS_ITEM_DURATION_ELEMENT_SELECTOR)
                    if week not in self.data["opening_hours"] and week.strip():
                        self.data["opening_hours"][week] = "/".join([e.text for e in durations])
            except NoSuchElementException:
                pass

            # check all fields were found
            if all(self.data.values()):
                return True
            return False

    class get_branch_url:
        """
        Find branch url of first search result.
        """
        def __call__(self, driver) -> Union[str, bool]:
            try:
                ele = driver.find_element(By.CSS_SELECTOR, PAGE_BRANCH_SELECTORS["search_highly_matched"])
                return ele.get_attribute("href")
            except NoSuchElementException:
                try:
                    ele = driver.find_element(By.CSS_SELECTOR, PAGE_BRANCH_SELECTORS["search_low_matched"])
                    return ele.get_attribute("href")
                except NoSuchElementException:
                    return False


class GoogleMapsBusinessCrawler:
    def __init__(self):
        self.driver = webdriver.Edge()
        self.driver.maximize_window()

    def __del__(self):
        self.driver.quit()

    def __fully_matched_case(self, timeout: int) -> Union[dict, bool]:
        """
        The page shows correct contents which we want.
        :param timeout: timeout seconds
        :return: data dictionary if any field was found successfully else False
        """
        data = {k: None for k in BUSINESS_DATA_FIELDS}
        data["opening_hours"] = {}  # init value of opening hours is an empty dict
        try:
            WebDriverWait(self.driver, timeout).until(CustomCondition.get_business_elements(data))
        except TimeoutException:
            pass
        if any(data.values()):
            return data
        return False

    def __partially_matched_case(self, timeout: int) -> Union[str, bool]:
        try:
            url = WebDriverWait(self.driver, timeout).until(CustomCondition.get_branch_url())
            return url
        except TimeoutException:
            return False

    def get_business(self, search_keywords: list):
        self.driver.get(BASE_URL + " ".join(search_keywords))

        # Try partially matched case first
        search_result_url = self.__partially_matched_case(1)

        if search_result_url:
            # Branch to the place page if current page is on search result page
            self.driver.get(search_result_url)

        # Try fully matched case if current page is on the place page
        data = self.__fully_matched_case(2)
        if isinstance(data, dict):
            data["map"] = parse.unquote(self.driver.current_url)  # 轉換網址編碼來縮短長度
            return data
        return data


# In[48]:


#根據travelking名稱爬取google評分
rating=[]
review=[]
for i in range(0,135):
    crawler = GoogleMapsBusinessCrawler()
    print(crawler.get_business([str(my_dict[i]["地点"]), str(my_dict[i]['地址'])]))
    a=crawler.get_business([str(my_dict[i]["地点"]), str(my_dict[i]['地址'])])
    #print(a['rating'])
    if(a!=False):
        if (a["rating"]==''):
            rating.append("None")
        else :
            rating.append(a['rating'])
        if (a["total_reviews"]==''):
            rating.append("None")
        else :
            review.append(a['total_reviews'])
    else:
        rating.append("None")
        review.append("None")


# In[52]:


print(rating)


# In[55]:


print(review)


# In[53]:


filename = 'taichungRating.csv'
# 写入CSV文件
with open(filename, 'w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    writer.writerow(['評分'])  # 写入标题行
    for item in rating:
        writer.writerow([item])


# In[54]:


filename = 'taichungReview.csv'
# 写入CSV文件
with open(filename, 'w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    writer.writerow(['評論數'])  # 写入标题行
    for item in review:
        writer.writerow([item])


# In[12]:


rating=['4.2', '4.3', None, '4.4', '4.4', '4.1', None, '4.2', '4.1', '5.0', '4.6', '4.5', '4.1', '4.3', '4.5', '4.2', '4.3', '4.2', '4.2', '4.2', '4.4', '4.2', '4.0', '4.4', '4.2', '4.6', '4.2', '3.7', '4.4', '4.5', '4.4', '4.0', '4.3', '4.2', '4.5', '4.3', '3.9', '4.2', '4.0', '4.5', '4.2', '4.5', '4.2', '4.3', '4.6', '4.2', '4.4', '4.2', None, '4.4', '3.1', '4.5', '4.4', '4.4', '4.1', '4.0', '4.3', '4.7', '4.4', '4.1', '4.1', '4.6', '4.4', '4.2', '4.0', '4.4', '4.4', '4.4', '4.1', '3.4', '4.1', '4.1', '4.7', '4.6', '4.5', '4.1', '4.3', '4.3', '3.9', '3.8', '4.1', '4.1', '4.1', '4.4', '4.5', '4.4', '4.1', '3.7', '4.8', '4.1', '4.4', '4.4', '4.2', '4.3', '4.6', '4.4', '4.3', '4.2', '4.5', '4.3', None, '4.4', None, '4.0', '4.1', '4.4', '4.1', '4.1', '4.2', '3.7', '4.3', '4.5', '4.2', '4.1', '4.4', '4.3', '4.5', '4.1', '4.0', '4.3', '4.8', '4.3', '4.7', '4.4', '4.5', '4.2', '3.8', '4.2', '4.5', '4.2', '4.4', '4.2', '4.2', '4.4']
review=['(13,194)', '(26,428)', None, '(2,802)', '(147)', '(5,279)', None, '(1,691)', '(310)', '(2)', '(13,125)', '(2,573)', '(5,052)', '(8,326)', '(1,612)', '(1,691)', '(41,815)', '(2,834)', '(3,793)', '(18,369)', '(660)', '(122)', '(2,635)', '(210)', '(1,017)', '(36,862)', '(2,214)', '(4,154)', '(807)', '(42,294)', '(9,551)', '(618)', '(75)', '(22,416)', '(264)', '(85,170)', '(688)', '(42)', '(1,366)', '(43)', '(874)', '(415)', '(6,088)', '(504)', '(20,240)', '(3,520)', '(18)', '(11,908)', None, '(9,898)', '(760)', '(1,136)', '(26,812)', '(18,416)', '(28,348)', '(1,632)', '(8,087)', '(3)', '(7)', '(14,209)', '(1,744)', '(13,256)', '(269)', '(2,452)', '(2,219)', '(414)', '(343)', '(1,900)', '(33)', '(5)', '(1,533)', '(1,533)', '(940)', '(4,470)', '(9,212)', '(428)', '(581)', '(5,699)', '(11)', '(540)', '(995)', '(2,295)', '(1,328)', '(1,413)', '(2,573)', '(533)', '(15,439)', '(11,319)', '(5,226)', '(11,863)', '(2,671)', '(1,441)', '(32,181)', '(7,267)', '(4,126)', '(1,220)', '(288)', '(279)', '(10,537)', '(847)', None, '(5,744)', None, '(30)', '(5,740)', '(3,954)', '(1,090)', '(2,699)', '(25,175)', '(141)', '(296)', '(35,634)', '(7,900)', '(712)', '(204)', '(8,904)', '(4,978)', '(2,974)', '(10,221)', '(3)', '(25,660)', '(3,560)', '(7,129)', '(1,852)', '(7,941)', '(4,458)', '(2,747)', '(29,421)', '(9,240)', '(545)', '(1,891)', '(1,545)', '(1,545)', '(8,273)']
print(len(rating))


# In[13]:


for i in range(0,len(rating)):
    if(rating[i]==None):
        rating[i]="0"


# In[14]:


for i in range(0,len(review)):
    if(review[i]==None):
        review[i]="0"


# In[15]:


numeric_rating = [float(x) for x in rating]
print(numeric_rating)


# In[35]:


import re
numeric_review = []

for item in review:
    numbers = re.findall(r'\d+', item)
    numeric_value = int(''.join(numbers))
    numeric_review.append(numeric_value)

print(numeric_review)


# In[18]:


import pandas as pd
from numpy import *
C=0
for i in range(0,len(numeric_rating)):
    C=C+numeric_rating[i]
C=C/len(numeric_rating)
print(C)


# In[32]:


def score(v,m,R,C):
    return (v/(v+m)*R)+(m/(m+v)*C)


# In[36]:


weighted_rating=[]
for i in range(0,len(numeric_rating)):
    if(numeric_review[i]<800):#小於不參考
        weighted_rating.append(0)
    else:
        se = score(numeric_review[i],800,numeric_rating[i],C)
        weighted_rating.append(se)


# In[37]:


print(weighted_rating)


# In[27]:


print(my_dict[103])


# In[29]:


for i in range(0,len(numeric_rating)):
    my_dict[i].update({"評分":numeric_rating[i]})


# In[30]:


for i in range(0,len(numeric_review)):
    my_dict[i].update({"評論數":numeric_review[i]})


# In[38]:


for i in range(0,len(numeric_rating)):
    my_dict[i].update({"推薦分數":weighted_rating[i]})


# In[42]:


print(my_dict)


# In[43]:


with open('taichung.csv', 'w', newline='', encoding='utf-8') as csvfile:
    fieldnames = ['地点', '类型', '人气', '地址', '描述', 'Px', 'Py', '評分', '評論數', '推薦分數']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    for key, value in my_dict.items():
        writer.writerow(value)


# In[40]:


sorted_dict = dict(sorted(my_dict.items(), key=lambda x: x[1]['推薦分數'], reverse=True))
print(sorted_dict)


# In[41]:


import csv
with open('taichungSorted.csv', 'w', newline='', encoding='utf-8') as csvfile:
    fieldnames = ['地点', '类型', '人气', '地址', '描述', 'Px', 'Py', '評分', '評論數', '推薦分數']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    for key, value in sorted_dict.items():
        writer.writerow(value)


# In[76]:


# 读取CSV文件 計算推薦分數
# 读取CSV文件 計算推薦分數
# 读取CSV文件 計算推薦分數
import pandas as pd
df = pd.read_csv("taichung.csv", encoding='big5')


# In[80]:


rating=[]
review=[]

for i in range(0,len(df)):
    rating.append(df.iloc[i]['評分'])
    review.append(df.iloc[i]['評論數'])


# In[81]:


C=0
for i in range(0,len(rating)):
    C=C+rating[i]
C=C/len(rating)


# In[82]:


def score(v,m,R,C):
    return (v/(v+m)*R)+(m/(m+v)*C)


# In[83]:


weighted_rating=[]
for i in range(0,len(rating)):
    if(review[i]<400):#評論低於400則 不推薦
        weighted_rating.append(0)
    else:
        se = score(review[i],400,rating[i],C)
        weighted_rating.append(se)


# In[87]:


site_dict={}
for i in range(0,len(df)):
    site_dict[i] = {"地点": df.iloc[i][0], "类型": df.iloc[i][1], "人气": df.iloc[i][2], "地址": df.iloc[i][3], "描述": df.iloc[i][4], "Px": df.iloc[i][5], "Py": df.iloc[i][6], '評分': df.iloc[i][7], '評論數': df.iloc[i][8], '推薦分數': weighted_rating[i]}
print(site_dict)


# In[89]:


import csv
with open('taichung_F.csv', 'w', newline='', encoding='utf-8') as csvfile:
    fieldnames = ['地点', '类型', '人气', '地址', '描述', 'Px', 'Py', '評分', '評論數', '推薦分數']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    for key, value in site_dict.items():
        writer.writerow(value)
# 读取CSV文件 計算推薦分數   
# 读取CSV文件 計算推薦分數
# 读取CSV文件 計算推薦分數


# In[ ]:




