import os
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

def sendSms(smsServer,smsToken,smsFrom,smsTo,smsMessage):
    requestUrl = f'https://{smsServer}/sms.do?from={smsFrom}&to={smsTo}&message={smsMessage}&format=json'
    requestHeader = {"Authorization": f"Bearer {smsToken}"}
    result = requests.get(requestUrl,headers=requestHeader)
    print(f'SmsAPI:{result}')

    return result


url = 'https://ul.uni.lodz.pl/course.php?rg=1300-C1819-W&group=13R18191DAZJ3WB&subject=1300-D1WBO12&cdyd=Z-18%2F19&full=1'
siteName = 'USOS - rejestracja zetonowa: Jezyk arabski (Z-18/19)'
wantedString = os.environ['SEARCH_STRING']

#agent = {'User-Agent': 'Google Spider'}
#resp = requests.get(url, headers=agent)
#soup = BeautifulSoup(resp.content, 'lxml')

#table = soup.find('div', class_='wrtext')
#rows = table.findAll('tr', class_='strong')


# $ export CHROME_PATH=/usr/bin/chrome
chrome_bin = os.environ['GOOGLE_CHROME_BIN']
#chrome_bin = '/usr/bin/google-chrome'
#print(f'chrome_bin: {chrome_bin}')

# $ export CHROME_DRIVER=~/Python/BtlWebScrapper/venv/chromedriver/chromedriver
#chrome_driver = '/usr/local/bin/chromedriver'
chrome_driver = os.environ['CHROMEDRIVER_PATH']
#print(f'chrome_driver: {chrome_driver}')

chrome_options = Options()
chrome_options.binary_location = chrome_bin
chrome_options.add_argument('--disable-gpu')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument("--headless")

# chrome driver logging
# outputdir='/home/user1'
# service_log_path = "{}/chromedriver.log".format(outputdir)
# service_args = ['--verbose']
# print(f'service_log: {service_log_path}')

driver = webdriver.Chrome(executable_path=chrome_driver,
#                           service_args=service_args,
#                           service_log_path=service_log_path,
                           chrome_options=chrome_options)
driver.get(url)

# wait for needed content to load
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
timeout = 5
neededElement = 'd_body'
try:
    element_present = EC.presence_of_element_located((By.ID, neededElement))
    WebDriverWait(driver, timeout).until(element_present)
    isPageLoaded = True
    print("Web page loaded completely")
except TimeoutException:
    isPageLoaded = False
    print ("Timed out waiting for page to load")

if isPageLoaded:
    message = None
    html = driver.page_source
    driver.close()
    soup = BeautifulSoup(html, 'lxml')
    table = soup.find('div', class_='wrtext')
    rows = table.findAll('tr', class_='strong')
    for r in rows:
        tdata = r.findAll('td')
        if tdata[4].text != wantedString:
            message = 'found'
else:
    message = 'Couldn\'t retrieve page contents'
    driver.close()

if message:
    smsServer1 = os.environ['SMS_SERVER1']
    smsServer2 = os.environ['SMS_SERVER2']
    smsToken = os.environ['SMS_TOKEN']
    smsFrom = os.environ['SMS_FROM']
    smsTo = os.environ['SMS_TO']
    smsMessage = f'ALARM from {siteName}, check details on https://ul.uni.lodz.pl/index.php'

    result = sendSms(smsServer1,smsToken,smsFrom,smsTo,smsMessage)
    if result.status_code != 200:
        result = sendSms(smsServer2,smsToken,smsFrom,smsTo,smsMessage)
    print(f'SmsAPI:{result.text}')
