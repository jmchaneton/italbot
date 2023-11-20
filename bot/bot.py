from seleniumwire import webdriver
from selenium.webdriver.chrome.service import Service

from selenium.common.exceptions import NoSuchElementException, ElementClickInterceptedException, TimeoutException
import time
from selenium.webdriver.common.by import By
import pandas as pd
import os
import argparse
import time
from datetime import datetime 
import pandas as pd
import numpy as np
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from seleniumwire import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import WebDriverException, NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from os import system



def maybe_login(driver):
    try:
        email_element = driver.find_element(By.XPATH, '//input[@id="login-email"]')
    except NoSuchElementException:
        return 
    email_element.send_keys("ichaneton@gmail.com")
    time.sleep(1)
    password_element = driver.find_element(By.XPATH, '//input[@id="login-password"]')
    time.sleep(1)
    password_element.send_keys("TataChaneton1980")
    time.sleep(1)
    driver.find_element(By.XPATH, '//button[@type="submit"]').click()

    # change to spanish
    try:
        WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.XPATH,  "//a[contains(text(),'SPA')]"))).click()
    except TimeoutException:
        pass

def send_email():
    os.system(
    """
    curl --request POST \
    --url https://api.courier.com/send \
    --header 'Authorization: Bearer pk_prod_YHY9BKCG7BM718MB6SF65GSXPQ68' \
    --data '{
      "message": {
        "to": {"email":"jmchaneton@gmail.com, juan@cimulate.ai, ichaneton@gmail.com", "phone_number": "+19176789106"},
        "content": {
          "title": "Turnos en el consulado disponibles!",
          "body": "Parece que hay turnos!!!!"
        },
        "data": {}
        }
    }'
    """
    )


def get_chrome_webdriver(proxy_index:int=None):

    opts = webdriver.ChromeOptions()
    opts.add_argument("--incognito")

    # if not settings.demo_mode:
    #     opts.add_argument("--headless")
    options_seleniumWire = None
    if proxy_index is not None:
        proxy = pd.read_csv('proxies', header=None).iloc[proxy_index, 0].split(':')
        proxy = f"http://{proxy[2]}:{proxy[3]}@{proxy[0]}:{proxy[1]}"
        options_seleniumWire = {
            'proxy': {
                'http': proxy,
            }
        }
        print(f'using proxy {proxy}')

    driver = webdriver.Chrome(service=Service(executable_path=ChromeDriverManager().install()),
                            seleniumwire_options=options_seleniumWire, options=opts)
    return driver

def try_clicking(driver, button_xpath, message_xpath, max_attempts, wait_time):
    attempts = 0
    reloads, max_reloads = 0, 3
    while attempts < max_attempts:
        
        maybe_login(driver)
        time.sleep(1)

        try:
            # Attempt to click the button
            button = driver.find_element(By.XPATH, button_xpath)
            button.click()

            # Wait for potential message to appear
            time.sleep(2)

            # Check for the message
            try:
                message = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.XPATH, message_xpath)))
                message = message.click()
                print(f"Attempt {attempts + 1}: Message found")
            except TimeoutException:
                print("Message not found!!. Sending email and stopping.")
                send_email()
                for _ in range(10):
                    system('say Turnos disponibles!')
                    time.sleep(1)
                while(True):
                    _ = input()
                
        except (NoSuchElementException, ElementClickInterceptedException):
            print(f"Attempt {attempts + 1}: Button not found or not clickable. Reloading")
            driver.get('https://prenotami.esteri.it/Services')
            maybe_login(driver)
            if reloads >= max_reloads:
                return attempts
            reloads += 1


        # Wait before next attempt
        time.sleep(wait_time)
        attempts += 1

    return None



def run_bot():

    parser = argparse.ArgumentParser(
        usage="run_bot --n_attempts <number of attempts>" 
    )
    parser.add_argument(
        "--n_attempts", required=False, default=1000, type=int
    )

    parser.add_argument(
        "-proxy", default=False, type=bool
    )

    args = parser.parse_args()

    # Use 'options' instead of 'chrome_options'
    proxy_index = 1 if args.proxy else None
    driver = get_chrome_webdriver(proxy_index)

    # Initialize the driver
    # driver = get_chrome_webdriver() # Replace with your webdriver path

    # Open the webpage
    driver.get('https://prenotami.esteri.it/Services') 

    time.sleep(5)

    #log in
    maybe_login(driver)

  
    # Configuration
    button_xpath = "/html/body//a[contains(@href,'224')]"  # Replace with your button's xpath
    message_xpath = "//button[contains(text(),'ok') and @class='btn btn-blue']"  # Replace with your message's xpath
    max_attempts = args.n_attempts  # Max number of attempts
    wait_time = 10   # Time to wait between attempts in seconds

    # Trying to click and check for message
    while True:
        n_attempts  = try_clicking(driver, button_xpath, message_xpath, max_attempts, wait_time)
        if n_attempts is not None and proxy_index is not None:
            max_attempts -= n_attempts
            print('Changing proxy')
            driver.quit()
            proxy_index += 1
            driver = get_chrome_webdriver(proxy_index)
            try_clicking(driver, button_xpath, message_xpath, max_attempts, wait_time)
        else:
            break

if __name__ == "__main__":
    run_bot()
