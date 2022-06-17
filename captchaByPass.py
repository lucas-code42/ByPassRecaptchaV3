from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup as BSHTML
from selenium import webdriver
import time,requests
import os


BY_PASS_URL = 'https://www.google.com/recaptcha/api2/demo'
IBM_WATSON = 'https://speech-to-text-demo.ng.bluemix.net/'
FILE_NAME = 'audio.mp3'
AUDIO_TO_TEXT_DELAY = 10
DELAY_TIME = 2


def save_file(content, filename):
    with open(filename, "wb") as file:
        for data in content.iter_content():
            file.write(data)

def audio_to_text(mp3Path):
    
    driver.execute_script('''window.open("","_blank");''')
    driver.switch_to.window(driver.window_handles[1])

    driver.get(IBM_WATSON)

    time.sleep(1)
    root = driver.find_element_by_id('root').find_elements_by_class_name('dropzone _container _container_large')
    btn = driver.find_element(By.XPATH, '//*[@id="root"]/div/input')
    btn.send_keys(mp3Path)

    time.sleep(AUDIO_TO_TEXT_DELAY)

    html = driver.page_source
    soup = BSHTML(html, 'html.parser')
    find_text = soup.find('div', attrs={'data-id': 'Text'})
    find_text = str(find_text)
    find_text = find_text.replace('<div data-id="Text"><div><span>', '')
    find_text = find_text.replace(' </span></div></div>', '')
    
    result = find_text

    driver.close()
    driver.switch_to.window(driver.window_handles[0])

    return result

def remove_mp3_file(filename):
    try:
        os.remove(filename)
        print('MP3 file was removed.')
    except:
        print('Could not remove MP3 file.')



if __name__ =='__main__':
    
    option = webdriver.ChromeOptions()
    option.add_argument('disable-infobars')
    option.add_argument('--disable-notifications')
    option.add_argument("--mute-audio")
    option.add_argument("user-agent=Mozilla/5.0 (iPhone; CPU iPhone OS 10_3 like Mac OS X) AppleWebKit/602.1.50 (KHTML, like Gecko) CriOS/56.0.2924.75 Mobile/14E5239e Safari/602.1")

    service = Service(executable_path='/home/lcs-42/Documents/studies/byPassRecaptchaV3/crhome/chromedriver') # your Chrome Driver path
    driver = webdriver.Chrome(service=service, options=option)

    driver.get(BY_PASS_URL)
    google = driver.find_elements_by_class_name('g-recaptcha')[0]
    iframe = google.find_element_by_tag_name('iframe')
    iframe.click()

    allIframesLen = driver.find_elements_by_tag_name('iframe')
    audioBtnFound = False
    audioBtnIndex = -1

    for index in range(len(allIframesLen)):
        driver.switch_to.default_content()
        iframe = driver.find_elements_by_tag_name('iframe')[index]
        driver.switch_to.frame(iframe)
        driver.implicitly_wait(DELAY_TIME)
        try:
            audioBtn = driver.find_element_by_id('recaptcha-audio-button') or driver.find_element_by_id('recaptcha-anchor')
            audioBtn.click()
            audioBtnFound = True
            audioBtnIndex = index
            break
        except Exception as e:
            pass

    if audioBtnFound:
        try:
            while True:
                href = driver.find_element_by_id('audio-source').get_attribute('src')
                response = requests.get(href, stream=True)
                save_file(response, FILE_NAME)
                response = audio_to_text(os.getcwd() + '/' + FILE_NAME)
                print(response)

                driver.switch_to.default_content()
                iframe = driver.find_elements_by_tag_name('iframe')[audioBtnIndex]
                driver.switch_to.frame(iframe)

                inputbtn = driver.find_element_by_id('audio-response')
                inputbtn.send_keys(response)
                inputbtn.send_keys(Keys.ENTER)

                time.sleep(2)
                errorMsg = driver.find_elements_by_class_name('rc-audiochallenge-error-message')[0]

                if errorMsg.text == "" or errorMsg.value_of_css_property('display') == 'none':
                    os.system('clear')
                    remove_mp3_file(FILE_NAME)
                    print("Captcha was broken with success!")
                break
        except Exception as ex:
            os.system('clear')
            print(ex)
            print('Warnig. Need to change proxy now.')
    else:
        os.system('clear')
        print('Button not found. This should not happen.')


