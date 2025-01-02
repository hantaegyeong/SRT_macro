from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select
from datetime import datetime, timedelta
import time

today = datetime.now()
tomorrow = today + timedelta(days=1)  # 날짜 설정은 내일로 되어있음
formatted_tomorrow = tomorrow.strftime("%Y%m%d")  # YYYYMMDD 형식

service = ChromeService(executable_path="C:\\chromedriver-win64\\chromedriver.exe")
driver = webdriver.Chrome(service=service)

driver.get('https://etk.srail.kr/cmc/01/selectLoginForm.do?pageId=TK0701000000')
driver.implicitly_wait(15)

driver.find_element(By.ID, 'srchDvNm01').send_keys('') # 회원번호
driver.find_element(By.ID, 'hmpgPwdCphd01').send_keys("") # 비밀번호

driver.find_element(By.XPATH, '//*[@id="login-form"]/fieldset/div[1]/div[1]/div[2]/div/div[2]/input').click()
driver.implicitly_wait(5)

driver.get('https://etk.srail.kr/hpg/hra/01/selectScheduleList.do')
driver.implicitly_wait(5)


# 출발지 입력
dep_stn = driver.find_element(By.ID, 'dptRsStnCdNm')
dep_stn.clear() 
dep_stn.send_keys("동대구")

# 도착지 입력
arr_stn = driver.find_element(By.ID, 'arvRsStnCdNm')
arr_stn.clear()
arr_stn.send_keys("부산")

driver.find_element(By.ID, "dptDt").click()
Select(driver.find_element(By.ID, "dptDt")).select_by_value(formatted_tomorrow)

driver.find_element(By.ID, "dptTm").click()
Select(driver.find_element(By.ID, "dptTm")).select_by_value("000000")

driver.find_element(By.XPATH,"//input[@value='조회하기']").click()

train_list = driver.find_elements(By.CSS_SELECTOR, '#result-form > fieldset > div.tbl_wrap.th_thead > table > tbody > tr')

print(len(train_list))

train_data = []

reserved = False

while True:
    for i in range(1, 5):
        standard_seat = driver.find_element(By.CSS_SELECTOR, f"#result-form > fieldset > div.tbl_wrap.th_thead > table > tbody > tr:nth-child({i}) > td:nth-child(7)").text

        if "예약하기" in standard_seat:
            print("예약 가능")          
            driver.find_element(By.XPATH, f"/html/body/div[1]/div[4]/div/div[3]/div[1]/form/fieldset/div[6]/table/tbody/tr[{i}]/td[7]/a/span").click()
            reserved = True
            break

    if not reserved:
       
        time.sleep(5)
        
        submit = driver.find_element(By.XPATH, "//input[@value='조회하기']")
        driver.execute_script("arguments[0].click();", submit)
        print("새로고침")

        driver.implicitly_wait(10)
        time.sleep(1)
    else:
        break

time.sleep(20)