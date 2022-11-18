from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from time import sleep
from selenium.common.exceptions import NoSuchElementException, ElementNotInteractableException
from selenium.webdriver.common.keys import Keys
import pandas as pd
import requests
import warnings
warnings.filterwarnings('ignore', category=DeprecationWarning)

class base_info_crawler():
    
    def __init__(self,url,path) :
        self.url = url
        self.driver = webdriver.Chrome(executable_path=path)
        options = webdriver.ChromeOptions()
        options.add_argument('window-size=1920,1080')


    def get_data(self,num):
        title, price, reviews_link, product_link , amazon_choice, best_seller, category = [],[],[],[],[],[],[]
        
        self.driver.get(self.url)
        
        # Delivery Location Setting --> 임의로 Los Angeles(zipcode=90001) 설정
        self.loc_btn = self.driver.find_element_by_id('glow-ingress-line2').click()
        sleep(1)
        self.type = self.driver.find_element_by_id('GLUXZipUpdateInput').send_keys('90001')
        self.apply = self.driver.find_element_by_xpath('//*[@id="GLUXZipUpdate"]/span').click()
        sleep(1)
        self.done = self.driver.find_element_by_xpath('//*[@id="a-popover-2"]/div/div[2]/span/span').click()  # popover --> 1또는2 랜덤생성인듯
        sleep(1)
        
        for i in range(1,num):
            
            # 크롤링할 페이지 수정
            self.driver.get(self.url+f'&page={i}&qid=1648177015&ref=sr_pg_{i}')
            sleep(1)
            
            # Scroll Down 
            body = self.driver.find_element_by_css_selector('body')
            for j in range(10):
                body.send_keys(Keys.PAGE_DOWN)
                sleep(0.5)
            
            # Crawl_start
            html = self.driver.page_source
            self.soup = BeautifulSoup(html,'html.parser')
            
            # all_info --> sponsored 거른 나머지 아이템들 수집하는 태그!
            all_info = self.soup.find_all('div', {'class' : "sg-col-4-of-12 s-result-item s-asin sg-col-4-of-16 sg-col s-widget-spacing-small sg-col-4-of-20"})
            
            for info in range(len(all_info)):
                
                # category --> 매번 변경해야하는 문제점 존재
                category.append('Sports and Outdoors')
                
                # title
                try:
                    title.append(all_info[info].find_all('span', {'class':'a-size-base-plus a-color-base a-text-normal'})[0].get_text().replace('\n',''))
                except:
                    title.append(None)
                
                # price
                try:
                    price.append(all_info[info].find_all('span', {'class' : 'a-offscreen'})[0].get_text())
                except:
                    price.append(None)  
                    
                # product_link
                try:
                    self.pl = all_info[info].find_all('a', {'class' : 'a-link-normal s-underline-text s-underline-link-text s-link-style a-text-normal'})[0].get('href')
                    # self.pl --> product_link
                    product_link.append('https://www.amazon.com/' + self.pl)
                except:
                    product_link.append(None)               
                
                # reviews_link
                try:
                    self.content = self.pl.split('/')[1]+'/dp'
                    self.rl = self.pl.replace(self.content,'product-reviews')
                    reviews_link.append('https://www.amazon.com/' + self.rl)
                except:
                    reviews_link.append(None)
                    
                # amazon_choice & Best Seller
                # 배지가 있으면 0, 있으면 1로 통일
                # 2개 배지를 다 가진 아이템X
                
                self.badge = all_info[info].find('span',attrs={'class' : 'a-badge-label-inner a-text-ellipsis'})
                if self.badge:
                    if self.badge.get_text() == "Amazon's Choice":
                        amazon_choice.append(1)
                        best_seller.append(0)
                    
                    elif self.badge.get_text() == "Best Seller":
                        best_seller.append(1)
                        amazon_choice.append(0)
                    else:
                        best_seller.append(0)
                        amazon_choice.append(0)
                else:
                    amazon_choice.append(0)
                    best_seller.append(0)
                
            if i % 100 == 0:
                print(f'{i}번째 페이지 수집 완료!')
            
        amazon_base_df = pd.DataFrame({'Category' : category,'Product_Name' : title, 'Price': price, 
                            'Product_link' : product_link, 'Review_link' : reviews_link, 
                            "Amazon_choice": amazon_choice, "Best_seller": best_seller})
        
        return amazon_base_df
        
 
#url = 'https://www.amazon.com/s?i=electronics-intl-ship&bbn=16225009011&rh=n%3A16225009011%2Cn%3A2811119011' --> cp_acc
#url = 'https://www.amazon.com/s?rh=n%3A16225014011&fs=true&ref=lp_16225014011_sar'  --> sports and outdoors
# url가져오는 건 한국으로 Delivery Location 설정 후 카테고리 선택 --> See all Results --> url 변수에 링크 입력


if __name__ == '__main__':
    print('------------base_crawler 실행------------')
    url = 'https://www.amazon.com/s?rh=n%3A16225014011&fs=true&ref=lp_16225014011_sar'
    path = '/Users/ryu/Desktop/crawl_study/amazon_crawler/chromedriver'
    
    amazon_base_df = base_info_crawler(url,path).get_data(401)
    amazon_base_df.to_csv('sports_and_outdoor_base.csv',index=False)