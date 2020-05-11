from selenium import webdriver
from PIL import Image,ImageEnhance
from selenium.webdriver.common.keys import Keys
# from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.select import Select
import time
import pytesseract
import re
import sys

pytesseract.pytesseract.tesseract_cmd = r'/usr/local/Cellar/tesseract/4.1.1/bin/tesseract'
page_shot = './page_shot.png'

city1 = '' # 城市选择中左边的项目,在引号内修改
city2 = '' # 城市选择中右边的项目,在引号内修改,如果是上海,需要输入在宿舍或不在宿舍,希望你还记得:)
username = '' # 输入登录ID,在引号内更改
password = '' # 输入登录密码,在引号内更改

def first_username_login(driver):
    try:
        driver.find_element_by_xpath("//div[@class='tab_option user-login']").click()
        return True
    except:
        return True

def get_imageCode(driver):
    # 识别验证码并自动填写
    code = 1
    imagesrc = driver.find_element_by_id('codeImg').find_element_by_tag_name('img').get_attribute('src')
    # print(imagesrc)
    # 判断是否存在验证码
    if re.match(r"https://login.sufe.edu.cn/cas/codeimage.*", imagesrc):
        # 截图网页(因为下载验证码会导致一个随机变化)
        driver.get_screenshot_as_file(page_shot)

        location = driver.find_element_by_id('codeImg').location
        size = driver.find_element_by_id('codeImg').size
        x0 = location['x']*2
        y0 = (location['y'] + 2)*2
        x1 = (location['x'] + size['width'] - 2)*2
        y1 = (location['y'] + size['height'])*2
        # print((x0,y0,x1,y1))
        # 从文件读取截图，截取验证码位置再次保存
        img = Image.open(page_shot).crop((x0,y0,x1,y1))
        img = img.convert('L')
        # 增加对比度
        enh_con = ImageEnhance.Contrast(img)
        contrast = 2.0
        img = enh_con.enhance(contrast)
        # 引用自动识别验证码库
        code = pytesseract.image_to_string(img)
        # img.save(page_shot)
    return code

def auto_login(driver, username, password):
    try:
        while re.match(r'https://login.sufe.edu.cn/cas/login.*', driver.current_url):
            if first_username_login(driver):
                driver.find_element_by_id('username').send_keys(username)
                driver.find_element_by_id('password').send_keys(password)
                code = get_imageCode(driver)
                # print(code)
                driver.find_element_by_id('imageCodeName').send_keys(code)
                time.sleep(1)
                driver.find_element_by_id('submitButton').click()
            # print(driver.current_url)
            time.sleep(1)
        if re.match(r'http://eams.sufe.edu.cn/tch/ncp.*', driver.current_url):
            driver.send_keys(Keys.ENTER)
        return
    except:
        print("出现了一点bug,拜托重新运行一下程序吧:),如果程序还在运行,请忽略")

def  find_all_NULL(driver):
    # 勾选所有“否”选项
    for item in driver.find_elements_by_xpath("//div[@class='weui-cell__bd']//p[text()='否']"):
        if item.is_displayed():
            item.click()
    time.sleep(2)

def fill_city(driver):
    city = city1+'-'+city2
    city_button = driver.find_element_by_id('city_name')
    driver.execute_script("arguments[0].value = '{}';".format(city), city_button)

def submit(driver):
    driver.find_element_by_id('submit').click()
    time.sleep(5)
    driver.find_element_by_id('cofirmSubmit').click()
    time.sleep(2)

def main():
    driver = webdriver.Chrome()
    driver.get('http://eams.sufe.edu.cn/tch/ncp/ncpIndex.jsp')

    auto_login(driver, username, password)
    time.sleep(1)
    find_all_NULL(driver)
    fill_city(driver)
    time.sleep(3)
    submit(driver)
    driver.quit()

main()