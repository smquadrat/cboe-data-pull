from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
import time
import csv
import os
import pandas as pd

from tqdm import tqdm

'''
UPDATE Guide (use Selenium Chrome plugin to inspect CSS):
1. View Chain Button (update [] portion below):
driver.find_element(By.CSS_SELECTOR, ".[bSXhTz] > .Button__TextContainer-sc-1tdgwi0-1").click()

2. Find Download Button (update [] portion below):
    element = driver.find_element(By.CSS_SELECTOR, ".[iNjxgG]")
'''

def webdriver_setup(sector):
    directory_filepath = rf"C:\CBOE_Pull\CSV\{sector}"
    global driver
    options = webdriver.ChromeOptions()
    options.add_argument('log-level=3')
    options.add_experimental_option("prefs", {
    "download.default_directory": directory_filepath,
    "download.prompt_for_download": False,
    "download.directory_upgrade": True,
    "safebrowsing.enabled": True
    })
    driver = webdriver.Chrome(r'C:\CBOE_Pull\chromedriver.exe', chrome_options=options)
    return driver

def read_tracking_file(sector):
    global tracking_list
    tracking_list = []
    tracking_file = rf"C:\CBOE_Pull\CSV\_Tracking\{sector}.csv"
    
    with open(tracking_file) as inputfile:
        for row in csv.reader(inputfile):
            tracking_list.append(row[0])

def file_download(url):
    driver.get(url)

    if len(driver.find_elements_by_xpath("//div[@id='privacy-alert']/div/div/div/button[2]")) > 0:
        driver.find_element(By.XPATH, "//div[@id='privacy-alert']/div/div/div/button[2]").click()

    driver.implicitly_wait(25)
    if 'No options' in driver.page_source:
        return print(str(url) + ' no options available')
    driver.find_element(By.XPATH, "//div[@id=\'root\']/div/div/div[2]/div[2]/div[2]/div[2]/div[3]/div/div[2]/div/div/div/div/div").click()
    driver.find_element(By.ID, "react-select-4-option-0").click()
    driver.find_element(By.XPATH, "//div[@id=\'root\']/div/div/div[2]/div[2]/div[2]/div[2]/div[4]/div/div[2]/div/div/div/div").click()
    driver.find_element(By.ID, "react-select-6-option-0").click()
    driver.find_element(By.CSS_SELECTOR, ".ijKPmP > .Button__TextContainer-sc-1tdgwi0-1").click()

    time.sleep(5)

    element = driver.find_element(By.CSS_SELECTOR, ".iNjxgG")
    hover = ActionChains(driver)
    hover.move_to_element(element).click().perform()

def data_pull(sector):
    pull_error_list = []
    webdriver_setup(sector)
    read_tracking_file(sector)
    directory_filepath = rf"C:\CBOE_Pull\CSV\{sector}"
    for stock in tqdm(tracking_list):
        try:
            base_path_components = (directory_filepath, 'TICK_quotedata.csv')
            base_path = "/".join(base_path_components)
            file_path = base_path.replace("TICK", str(stock))
            if os.path.exists(file_path):
                print(str(stock) + ' file exists')
            else:
                url = rf"https://www.cboe.com/delayed_quotes/{stock}/quote_table"
                file_download(url)
                if os.path.exists(file_path):
                    print(str(stock) + ' file exists')
        except Exception:
            print('Error: ' + str(stock))
            pull_error_list.append(stock)
    return pull_error_list

def data_check(sector):
    pull_error_list = []
    attempts = 1
    while pull_error_list != [] or attempts < 2:
        pull_error_list = data_pull(sector)
        attempts += 1

if __name__ == "__main__":
    sector_list = {1: '_main', 2: 'sectors', 3: 'tech', 4: 'cons_disc', 5: 'industrials', 6: 'communication', 7: 'financials', 8: 'energy'}
    def get_sector(choices):
        while True:
            sector_choice = int(input('Select one: 1) Main 2) Sectors 3) Tech 4) Consumer Discretionary 5) Industrials 6) Communication 7) Financials 8) Energy: '))
            if sector_choice in range(1, len(choices) + 1):
                sector = choices[sector_choice]
                return sector
    sector = get_sector(sector_list)
    pull_error_list = data_check(sector)
    print('Pull error list: ', pull_error_list)