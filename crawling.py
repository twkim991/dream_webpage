from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
import time

# 전역변수 선언 및 초기화
URL = "https://m.bunjang.co.kr/categories/600200?&req_ref=popular_category"
my_arr = []      # 정제된 데이터를 저장할 array
is_first = True  # 프로그램을 처음 실행시켰는지 여부
excepts = ["삽니다", "매입", "구매", "구입"]  # 1개라도 포함되면 안됨


# 크롬드라이버 실행
driver = webdriver.Chrome() 
driver.get(URL)
time.sleep(3)

# Chrome 옵션 설정
options = webdriver.ChromeOptions()
options.add_argument("headless")

# 크롬드라이버 실행
driver = webdriver.Chrome(options=options)

try:
    driver.get(URL)
    time.sleep(3)

    # 웹 페이지가 로드될 때까지 대기
    wait = WebDriverWait(driver, 10)
    wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="root"]/div/div/div[4]/div/div[4]')))

    # 데이터 수집
    elements = driver.find_elements(By.XPATH, '//*[@id="root"]/div/div/div[4]/div/div[4]')
    data = [element.text for element in elements]
    print(data)


finally:
    # WebDriver 종료
    driver.quit()