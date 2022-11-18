from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from time import sleep
from pandas import DataFrame
from selenium.common.exceptions import NoSuchElementException, ElementNotInteractableException
from selenium.webdriver.common.keys import Keys
import pandas as pd
import re
import random
import requests
import warnings
warnings.filterwarnings('ignore', category=DeprecationWarning)

amazon_base_df = pd.read_csv('sports_and_outdoor_base.csv')

class product_info_crawler():
    
    def __init__(self,path) :
        self.url = amazon_base_df['Product_link'][0]
        self.driver = webdriver.Chrome(executable_path=path)
        options = webdriver.ChromeOptions()
        options.add_argument('window-size=1920,1080')
    
    def get_data(self):
        product_link, item_rating, item_rating_count, item_answered_question, item_asin = [], [], [], [], []
        
        self.driver.get(self.url)
        
        # Delivery Location Setting --> 임의로 Los Angeles(zipcode=90001) 설정
        self.loc_btn = self.driver.find_element_by_id('glow-ingress-line2').click()
        sleep(random.uniform(1,2))
        self.type = self.driver.find_element_by_id('GLUXZipUpdateInput').send_keys('90001')
        self.apply = self.driver.find_element_by_xpath('//*[@id="GLUXZipUpdate"]/span').click()
        sleep(random.uniform(1,2))
        self.done = self.driver.find_element_by_xpath('//*[@id="a-popover-2"]/div/div[2]/span/span').click()  # popover --> 1또는2 랜덤생성인듯
        sleep(random.uniform(1,2))
        
        
        # 9,600개 나누고 마지막에 concatenate
        # 3,000개당 약 4시간 소요
        # (3000) , (3000,5000), (5000,7000), (7000,9000), (9000,9600)
        for page in range(5000, 7000):
            
            self.driver.get(amazon_base_df['Product_link'][page])
            sleep(random.uniform(1,2))
            html = self.driver.page_source
            self.soup = BeautifulSoup(html,'html.parser')
                        
            # product_link는 merge를 위해 수집
            product_link.append(amazon_base_df['Product_link'][page])
            
            # item_rating
            
            try:
                rating = self.soup.find('span', attrs={'class' : 'a-size-medium a-color-base'})
                item_rating.append(rating.get_text().split(' ')[0])
            except:
                item_rating.append(None)
                
            # item_rating_count
            try:
                rating_count = self.soup.find('span', attrs={'id' : 'acrCustomerReviewText'})
                item_rating_count.append(rating_count.get_text().split(' ')[0])
            except:
                item_rating_count.append(None)
            
            # item_answered_question
            
            item_qna_count = self.soup.find('a',attrs={'class' : 'a-link-normal askATFLink'})
            
            if item_qna_count:
                item_qna_count = item_qna_count.find('span',attrs={'class' : 'a-size-base'})
                item_qna_count = item_qna_count.get_text().split(' ')[1]
                remove_plus = re.sub('[^0-9]','',item_qna_count)
                item_answered_question.append(remove_plus)
            
            else:
                item_answered_question.append(None)

            # ASIN --> Product링크에서 추출
            asin_code = amazon_base_df['Product_link'][page].split('/')[6]
            item_asin.append(asin_code)

            if page % 10 == 0:
                print(f'{page}번째 상품 수집 완료!')
            
        amazon_product_df = pd.DataFrame({'Product_link' : product_link, 'Item_Rating': item_rating, 
                            'Item_Rating_Count' : item_rating_count, 'Item_Answered_Question' : item_answered_question, 
                            "ASIN": item_asin}) 
            
        return amazon_product_df


if __name__ == '__main__':
    print('-------------product_info_crawler실행-------------')
    path = '/Users/ryu/Desktop/crawl_study/amazon_crawler/chromedriver'
    amazon_product_df_5 = product_info_crawler(path).get_data()
    amazon_product_df_5.to_csv('so_product_df_3.csv',index=False)