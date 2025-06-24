import tkinter as tk
from tkinter import ttk
import tkinter.font as tkfont
from tkcalendar import Calendar
from PIL import Image, ImageTk
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from datetime import datetime
import time
import sys
import os

station_list = ["수서", "동탄", "평택지제", "대전", "동대구", "부산", "울산(통도사)", "포항"]
station_code = {
    "수서": "0551", "동탄": "0552", "평택지제": "0553",
    "대전": "0010", "동대구": "0015", "부산": "0020",
    "울산(통도사)": "0509", "포항": "0515"
}
time_dict = {
    "00:00": "000000", "02:00": "020000", "04:00": "040000",
    "06:00": "060000", "08:00": "080000", "10:00": "100000",
    "12:00": "120000", "14:00": "140000", "16:00": "160000",
    "18:00": "180000", "20:00": "200000", "22:00": "220000"
}

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

def start_booking():
    result_label.config(text="🚀 예약 진행 중...")
    dep_station = dep_var.get()
    arr_station = arr_var.get()
    dep_code = station_code.get(dep_station, "")
    arr_code = station_code.get(arr_station, "")
    login_info = login_input_var.get()
    password = pass_var.get()
    selected_date = datetime.strptime(cal.get_date(), "%Y-%m-%d").strftime("%Y.%m.%d")

    selected_time_str = time_var.get()
    if selected_time_str not in time_dict:
        result_label.config(text="⚠ 출발 시각을 선택하세요.")
        return
    selected_time = time_dict[selected_time_str]

    people_count = people_var.get()
    children_count = children_var.get()
    senior_count = senior_var.get()

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    try:
        driver.get('https://etk.srail.kr/cmc/01/selectLoginForm.do?pageId=TK0701000000')
        driver.implicitly_wait(15)
        driver.find_element(By.ID, "srchDvCd1").click()
        driver.find_element(By.ID, "srchDvNm01").send_keys(login_info)
        driver.find_element(By.ID, "hmpgPwdCphd01").send_keys(password)
        driver.find_element(By.XPATH, "//input[@type='submit' and @value='확인']").click()

        try:
            WebDriverWait(driver, 3).until(EC.alert_is_present()).accept()
            result_label.config(text="❌ 로그인 실패: 알림창 발생")
            driver.quit()
            return
        except:
            pass

        driver.get('https://etk.srail.kr/hpg/hra/01/selectScheduleList.do')
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "dptRsStnCdNm")))
        driver.find_element(By.ID, "dptRsStnCdNm").send_keys(dep_station)
        driver.execute_script("document.getElementsByName('dptRsStnCd')[0].value = arguments[0];", dep_code)
        driver.find_element(By.ID, "arvRsStnCdNm").send_keys(arr_station)
        driver.execute_script("document.getElementsByName('arvRsStnCd')[0].value = arguments[0];", arr_code)
        Select(driver.find_element(By.ID, "dptDt")).select_by_value(selected_date.replace(".", ""))
        Select(driver.find_element(By.ID, "dptTm")).select_by_value(selected_time)
        Select(driver.find_element(By.ID, "psgInfoPerPrnb1")).select_by_value(people_count)
        Select(driver.find_element(By.ID, "psgInfoPerPrnb5")).select_by_value(children_count)
        Select(driver.find_element(By.ID, "psgInfoPerPrnb4")).select_by_value(senior_count)

        driver.find_element(By.ID, "trnGpCd300").click()
        driver.find_element(By.CLASS_NAME, "inquery_btn").click()
        time.sleep(2)

        reserved = False
        for i in range(1, 6):
            try:
                reserve_a = driver.find_element(By.XPATH, f"/html/body/div[1]/div[4]/div/div[3]/div[1]/form/fieldset/div[6]/table/tbody/tr[{i}]/td[7]/a")
                onclick = reserve_a.get_attribute("onclick")
                if onclick:
                    driver.execute_script("window.hasClassName = function() { return true; }")
                    try:
                        driver.execute_script(onclick)
                        time.sleep(2)
                        WebDriverWait(driver, 3).until(EC.presence_of_element_located((By.ID, "resveDt")))
                        reserved = True
                        break
                    except:
                        try:
                            driver.switch_to.alert.accept()
                            reserved = True
                            break
                        except:
                            continue
            except:
                continue

        if reserved:
            result_label.config(text="✅ 예약 성공! 홈페이지에서 결제해주세요.")
        else:
            result_label.config(text="❌ 예약 가능한 열차 없음")

    except Exception as e:
        result_label.config(text=f"⚠ 오류 발생: {str(e)}")
    finally:
        driver.quit()

app = tk.Tk()
app.title("🚆SRT 예매 도우미")
app.geometry("600x700")
app.configure(bg="white")

default_font = tkfont.Font(family="맑은 고딕", size=11)
app.option_add("*Font", default_font)

img = Image.open(resource_path("srt_header2.png"))
img = img.resize((600, int(img.height * 600 / img.width)))
photo = ImageTk.PhotoImage(img)
img_label = tk.Label(app, image=photo, bg="white")
img_label.pack(pady=(0, 50))

main_frame = tk.Frame(app, bg="white")
main_frame.pack(pady=10)

left_frame = tk.Frame(main_frame, bg="white")
left_frame.grid(row=0, column=0, padx=20, sticky="n")

tk.Label(left_frame, text="회원번호:", bg="white").pack(anchor="w")
login_input_var = tk.StringVar()
tk.Entry(left_frame, textvariable=login_input_var).pack()

tk.Label(left_frame, text="비밀번호:", bg="white").pack(anchor="w")
pass_var = tk.StringVar()
tk.Entry(left_frame, textvariable=pass_var, show="*").pack()

tk.Label(left_frame, text="출발역:", bg="white").pack(anchor="w")
dep_var = tk.StringVar()
ttk.Combobox(left_frame, textvariable=dep_var, values=station_list).pack()

tk.Label(left_frame, text="도착역:", bg="white").pack(anchor="w")
arr_var = tk.StringVar()
ttk.Combobox(left_frame, textvariable=arr_var, values=station_list).pack()

tk.Label(left_frame, text="어른 수:", bg="white").pack(anchor="w")
people_var = tk.StringVar(value="1")
ttk.Combobox(left_frame, textvariable=people_var, values=[str(i) for i in range(10)]).pack()

tk.Label(left_frame, text="어린이 수:", bg="white").pack(anchor="w")
children_var = tk.StringVar(value="0")
ttk.Combobox(left_frame, textvariable=children_var, values=[str(i) for i in range(10)]).pack()

tk.Label(left_frame, text="경로 수:", bg="white").pack(anchor="w")
senior_var = tk.StringVar(value="0")
ttk.Combobox(left_frame, textvariable=senior_var, values=[str(i) for i in range(10)]).pack()

right_frame = tk.Frame(main_frame, bg="white")
right_frame.grid(row=0, column=1, padx=20, sticky="n")

tk.Label(right_frame, text="출발 시각:", bg="white").pack(anchor="w")
time_var = tk.StringVar(value="06:00") 
ttk.Combobox(right_frame, textvariable=time_var, values=list(time_dict.keys())).pack()

tk.Label(right_frame, text="출발 날짜:", bg="white").pack(anchor="w")
cal = Calendar(right_frame, selectmode="day", date_pattern="yyyy-mm-dd")
cal.pack()

footer_label = tk.Label(app, text="srt_macro by han", bg="white", fg="gray", font=("맑은 고딕", 9))
footer_label.pack(side="bottom", pady=(0, 10))

tk.Button(app, text="🚆 열차 조회 및 예약", bg="#800020", fg="white", command=start_booking, width=30, height=4).pack(pady=30)

result_label = tk.Label(app, text="", bg="white", font=("Arial", 11))
result_label.pack()

app.mainloop()
