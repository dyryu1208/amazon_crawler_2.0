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

amazon_product_df = pd.read_csv('cellphone_acc_product_2.csv',encoding='latin_1')

class review_cralwer():
    
    def __init__(self,path):
        self.url = amazon_product_df['Review_link'][0]
        self.driver = webdriver.Chrome(executable_path=path)
        options = webdriver.ChromeOptions()
        options.add_argument('window-size=1920,1080')
    
    def get_data(self):
        product_link, user_name, item_review_count, review_rating, review_verified = [],[],[],[],[]
        review_title, review_text, review_date, review_helpfulness = [],[],[],[]
        review_photo, review_video = [],[]
        
        self.driver.get(self.url)
        
        # Delivery Location Setting(Default)
        self.loc_btn = self.driver.find_element_by_id('glow-ingress-line2').click()
        sleep(random.uniform(1,2))
        self.type = self.driver.find_element_by_id('GLUXZipUpdateInput').send_keys('90001')
        self.apply = self.driver.find_element_by_xpath('//*[@id="GLUXZipUpdate"]/span').click()
        sleep(random.uniform(1,2))
        self.done = self.driver.find_element_by_xpath('//*[@id="a-popover-1"]/div/div[2]/span/span').click()
        sleep(random.uniform(1,2))       
        
        
        #for product in range(len(amazon_product_df)):
        for product in range(970,980):
            link = amazon_product_df['Review_link'][product]
            rating = amazon_product_df['Item_Rating_Count'][product]
            
            if rating is not None:
                self.driver.get(link)
                sleep(random.uniform(1,2))
                html = self.driver.page_source
                self.soup = BeautifulSoup(html,'html.parser')
                
                # Most Recent Setting
                self.sort_btn = self.driver.find_element_by_xpath('//*[@id="a-autoid-3-announce"]')
                self.sort_btn.click()
                sleep(2)
                self.mr_btn = self.driver.find_element_by_id('sort-order-dropdown_1').click()
                sleep(2)
                self.driver.refresh()  # 갑자기 한글 뜨길래 새로고침
                sleep(1)
                
                
                review_count = int(self.soup.find_all('div',{'id':'filter-info-section'})[0].get_text().replace(',', '').replace('|', '').strip().split()[3])
                
                # 1page에 리뷰 10개
                # page = review_count / 10
                
                if review_count % 10 == 0:
                    page = int(review_count/10)
                else:
                    page = (review_count//10)+1
                
                # Review를 5,000개 넘게 수집하면 Amazon에서 끊기 때문에 500page까지만 수집 
                for j in range(min(page, 500)):  
                    if j > 1:
                        self.driver.get('{}'.format('https://www.amazon.com/' + self.soup.find_all('div', {'id': 'cm_cr-pagination_bar'})[0].find_all('a')[1].attrs['href']))
                    elif j == 1:
                        self.driver.get('{}'.format('https://www.amazon.com/' + self.soup.find_all('div', {'id': 'cm_cr-pagination_bar'})[0].find_all('a')[0].attrs['href']))
                        
                        
                    sleep(random.uniform(1,2))
                    html = self.driver.page_source
                    self.soup = BeautifulSoup(html, 'html.parser')
                    reviews = self.soup.find_all('div',{'class' : 'a-section review aok-relative'})  # 1 page에 있는 모든 리뷰(10개)
                    
                    for k in range(len(reviews)):
                        
                        # product_link
                        product_link.append(amazon_product_df['Product_link'][product])
                        
                        # item_review_count
                        item_review_count.append(review_count)

                        # user_name
                        try : 
                            user_name.append(reviews[k].find('span', {'class': 'a-profile-name'}).get_text())
                        except:
                            user_name.append(None)
                        
                        # review_rating
                        try : 
                            review_rating.append(reviews[k].find_all('span', {'class':'a-icon-alt'})[0].get_text().split()[0])
                        except:
                            review_rating.append(None)
                        
                        # review_title
                        try : 
                            review_title.append(reviews[k].find_all('div', {'class':'a-row'})[0].find_all('span')[3].get_text())
                        except:
                            review_title.append(None)
                            
                        # review text
                        try : 
                            review_text.append(self.soup.find_all('div', {'class': 'a-row a-spacing-small review-data'})[k].find('span').get_text().strip())
                        except:
                            review_text.append(None)
                            
                        # review photo(사진 개수)
                        try:
                            review_photo.append(len(self.soup.find_all('div', {'class': 'a-section celwidget'})[k].find_all('img', {'class': 'review-image-tile'})))
                        except:
                            review_photo.append(0)
                                                   
                        # review video  --> 리뷰1개에 하나씩만 업로드 가능
                        if reviews[k].find_all('video'):
                            review_video.append(1)
                        else:
                            review_video.append(0)
                       
                        # review_date
                        try : 
                            review_date.append(reviews[k].find('span', {'class': 'a-size-base a-color-secondary review-date'}).get_text().split("on ")[1])
                        except:
                            review_date.append(None)
                            
                        # review_verified
                        try:
                            reviews[k].find_all('span', {'class': 'a-size-mini a-color-state a-text-bold'})[0].get_text()
                            review_verified.append(1)
                        except:
                            review_verified.append(0)
                        
                        # review_helpfulness
                        # one --> 1로 바꾸기
                        helpful = self.soup.find_all('div', {'class': 'a-section celwidget'})[k].find('span', {'data-hook': 'helpful-vote-statement'})
                        if helpful:
                            if helpful.get_text().split()[0] == 'One':
                                review_helpfulness.append(1)
                            else : review_helpfulness.append(int(helpful.get_text().split()[0].replace(",", "")))
                        else:
                            review_helpfulness.append(0)

                    if j % 10 == 0:
                        print(f'{amazon_product_df["Product_Name"][product]} \t 리뷰 {j*10}개 수집 완료!')
            
            else:
                product_link.append(amazon_product_df['Product_link'][product])
                item_review_count.append(None)
                user_name.append(None)
                review_rating.append(None)
                review_verified.append(None)
                review_title.append(None)
                review_text.append(None)
                review_photo.append(None)
                review_video.append(None)
                review_date.append(None)
                continue
            
        amazon_review_df = pd.DataFrame({'Product_link' : product_link, 'Item_Review_Count' : item_review_count,
                                        'User_Name' : user_name, 'Review_Rating' : review_rating,
                                        'Review_Verified' : review_verified, 'Review_Title' : review_title,
                                        'Review_Text' : review_text, 'Review_Photo' : review_photo,
                                        'Review_Video' : review_video, 'Review_Date' : review_date,
                                        'Review_Helpfulness' : review_helpfulness})
        return amazon_review_df




if __name__ == '__main__':
    print('-------------review_crawler실행-------------')
    path = '/Users/ryu/Desktop/crawl_study/amazon_crawler/chromedriver'
    amazon_review_df = review_cralwer(path).get_data()
    amazon_review_df.to_csv('cellphone_acc_review_101.csv',index=False)