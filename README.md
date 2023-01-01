# amazon_crawler_2.0

[Amazon.com](https://www.amazon.com/ref=nav_logo)에서 제공하는 상품 및 리뷰 데이터에 대한 크롤링 코드
수집 순서는 아래와 같음.

1. [base_crawler](/Amazon_Crawler_v2.0_base_data.py) : 특정 카테고리 내 상품의 [상품명, 가격, 상품 링크, 리뷰 링크, Amazon's Choice 여부, Best Seller 여부]에 대해 크롤링, 단일 카테고리에서 약 1만개 수량의 상품 정보 크롤링 가능
2. [product_crawler](/Amazon_Crawler_v2.0_product_data.py) : base_crawler에서 수집한 상품에 대해 상품 링크에 접속하여 [평균 평점, 평점 등록 수, Q&A 개수, ASIN 코드]와 같은 정보를 수집
3. [review_data](/Amazon_Crawler_v2.0_review_data.py) : 수집된 상품에 대해 리뷰 링크에 접속하여 [리뷰 개수, 유저명, 유저별평점, 리뷰 제목, 리뷰 내용, 첨부 사진 및 동영상 개수, 리뷰 작성일, 리뷰 검증 여부, 리뷰 유용성]와 같은 정보를 수집. 단, 리뷰는 웹 프로그램상의 문제로 인해 상품 당 최대 5,000개까지만 수집 가능


* 상품 및 리뷰 정보의 원활한 수집을 위해 #Delivery Location Setting을 California(zip_code = 90001)로 설정하였음. 주소가 미국 외 지역으로 설정되어 있으면 가격, 리뷰 등이 원활하게 수집되지 않음