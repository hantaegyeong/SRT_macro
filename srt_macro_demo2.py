from tkinter import Tk, Label, Entry, Button, StringVar, ttk
from tkcalendar import DateEntry
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select
import time

def start_booking():
    dep_station = dep_var.get()
    arr_station = arr_var.get()
    user_id = user_var.get()
    password = pass_var.get()
    selected_date = date_var.get().replace("-", "")
    selected_time = time_dict[time_var.get()]
    people_count = people_var.get()
    children_count = children_var.get()
    senior_count = senior_var.get()
    service = ChromeService(executable_path="C:\\chromedriver-win64\\chromedriver.exe")
    driver = webdriver.Chrome(service=service)

    try:
        driver.get('https://etk.srail.kr/cmc/01/selectLoginForm.do?pageId=TK0701000000')
        driver.implicitly_wait(15)
        
        driver.find_element(By.ID, 'srchDvNm01').send_keys(user_id)
        driver.find_element(By.ID, 'hmpgPwdCphd01').send_keys(password)
        driver.find_element(By.XPATH, '//*[@id="login-form"]/fieldset/div[1]/div[1]/div[2]/div/div[2]/input').click()
        driver.implicitly_wait(5)

        driver.get('https://etk.srail.kr/hpg/hra/01/selectScheduleList.do')
        driver.implicitly_wait(5)

        dep_stn = driver.find_element(By.ID, 'dptRsStnCdNm')
        dep_stn.clear()
        dep_stn.send_keys(dep_station)

        arr_stn = driver.find_element(By.ID, 'arvRsStnCdNm')
        arr_stn.clear()
        arr_stn.send_keys(arr_station)

        driver.find_element(By.ID, "dptDt").click()
        Select(driver.find_element(By.ID, "dptDt")).select_by_value(selected_date)

        driver.find_element(By.ID, "dptTm").click()
        Select(driver.find_element(By.ID, "dptTm")).select_by_value(selected_time)

        # 사람 수 선택
        people_select = driver.find_element(By.XPATH, '/html/body/div[1]/div[4]/div/div[2]/form/fieldset/div[1]/div/ul/li[2]/div[2]/div[1]/select')
        Select(people_select).select_by_value(people_count)

        children_select = driver.find_element(By.XPATH, '/html/body/div[1]/div[4]/div/div[2]/form/fieldset/div[1]/div/ul/li[2]/div[2]/div[2]/select')
        Select(children_select).select_by_value(children_count)

        senior_select = driver.find_element(By.XPATH, '/html/body/div[1]/div[4]/div/div[2]/form/fieldset/div[1]/div/ul/li[2]/div[2]/div[3]/select')
        Select(senior_select).select_by_value(senior_count)

        if int(people_count) + int(children_count) + int(senior_count) > 9:
            result_label.config(text="\n총 인원 수는 9명을 초과할 수 없습니다.")
            return



        driver.find_element(By.XPATH, "//input[@id='trnGpCd300']").click()
        driver.find_element(By.XPATH, "//input[@value='조회하기']").click()

        reserved = False  

        for i in range(1, 5):  
            try:
                reserve_button = driver.find_element(By.XPATH, f"/html/body/div[1]/div[4]/div/div[3]/div[1]/form/fieldset/div[6]/table/tbody/tr[{i}]/td[7]/a/span")
                driver.execute_script("arguments[0].scrollIntoView(true);", reserve_button)
                time.sleep(1)
                driver.execute_script("arguments[0].click();", reserve_button)
                print(f"{i}번째 열차 예약 버튼 클릭 완료")
                reserved = True
                break
            except Exception as e:
                print(f"{i}번째 열차에서 예약 버튼 클릭 실패: {e}")
                continue

        if reserved:
            print("예약 완료!")
        else:
            print("예약 가능한 열차를 찾지 못했습니다.")    
        time.sleep(20)

    except Exception as e:
        result_label.config(text=f"에러 발생: {str(e)}")
    finally:
        driver.quit()

# Tkinter
app = Tk()
app.title("SRT 예매 도우미")
app.geometry("600x600")

# 시간 변환 딕셔너리
time_dict = {
    "00:00": "000000",
    "02:00": "020000",
    "04:00": "040000",
    "06:00": "060000",
    "08:00": "080000",
    "10:00": "100000",
    "12:00": "120000",
    "14:00": "140000",
    "16:00": "160000",
    "18:00": "180000",
    "20:00": "200000",
    "22:00": "220000"
}

# 사용자 입력 필드
Label(app, text="회원번호:").pack()
user_var = StringVar()
Entry(app, textvariable=user_var).pack()

Label(app, text="비밀번호:").pack()
pass_var = StringVar()
Entry(app, textvariable=pass_var, show="*").pack()

Label(app, text="출발역:").pack()
dep_var = StringVar()
Entry(app, textvariable=dep_var).pack()

Label(app, text="도착역:").pack()
arr_var = StringVar()
Entry(app, textvariable=arr_var).pack()

Label(app, text="인원 선택(최대 총 9명)").pack()

Label(app, text="어른 수:").pack()
people_var = StringVar()
people_dropdown = ttk.Combobox(app, textvariable=people_var, values=[str(i) for i in range(0, 10)])
people_dropdown.set("1")  
people_dropdown.pack()

Label(app, text="어린이 수:").pack()
children_var = StringVar()
children_dropdown = ttk.Combobox(app, textvariable=children_var, values=[str(i) for i in range(0, 10)])
children_dropdown.set("0")  
children_dropdown.pack()

Label(app, text="경로 수:").pack()
senior_var = StringVar()
senior_dropdown = ttk.Combobox(app, textvariable=senior_var, values=[str(i) for i in range(0, 10)])
senior_dropdown.set("0")  
senior_dropdown.pack()

Label(app, text="날짜 선택:").pack()
date_var = StringVar()
date_picker = DateEntry(app, textvariable=date_var, date_pattern="yyyy-mm-dd")
date_picker.pack()

Label(app, text="시간 선택:").pack()
time_var = StringVar()
time_dropdown = ttk.Combobox(app, textvariable=time_var, values=list(time_dict.keys()))
time_dropdown.set("00:00") 
time_dropdown.pack()

# 시작 버튼
Button(app, text="예약 시작", command=start_booking).pack()

# 결과 표시
result_label = Label(app, text="")
result_label.pack()

# Tkinter 실행
app.mainloop()
