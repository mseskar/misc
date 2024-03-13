import datetime
import json
import sys
from time import sleep

import undetected_chromedriver as uc

from logger import Log
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

# CONSTANTS
TIMEOUT = 30  # This number is the amount of times we will wait for an action


class SeleniumToolbox:
    def return_webdriver(self):
        Log.info('Launching new Selenium Web Driver.')
        if self.browser_name == 'Chrome':
            options = ChromeOptions()
            options.add_argument('--headless')  # Ensure GUI is off
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            return webdriver.Chrome(options=options)
        elif self.browser_name == 'Firefox':
            options = FirefoxOptions()
            options.add_argument('--headless')  # Ensure GUI is off
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            return webdriver.Firefox(options=options)
        elif self.browser_name == 'udChrome':
            return uc.Chrome()

    def go_to_mainpage(self):
        Log.info(f'Navigating to mainpage {self.mainpage_url}')
        self.browserWebDriver.get(self.mainpage_url)
        self.browserWebDriver.maximize_window()  # maximize window size
        self.wait_till_loaded()

    def _initialize_wait(self):
        self.wait = WebDriverWait(self.browserWebDriver, TIMEOUT)

    # Waits to proceed until the loading wheel is gone and page is fully loaded
    def wait_till_loaded(self):
        self._initialize_wait()
        max_retries = 10
        retries = 0
        while retries < max_retries:
            try:
                # once main div 'body' is found page is loaded
                self.wait.until(EC.presence_of_element_located((By.TAG_NAME, 'body')))
                Log.info(f'Page {self.browserWebDriver.current_url} loaded.')
                return True
            except:
                retries += 1
                continue
        return False

    def navigate(self, url):
        self.browserWebDriver.get(url)
        Log.info(f'Navigating to {url}')
        self.wait_till_loaded()

    def set_zoom(self, x):
        self.browserWebDriver.execute_script(f"document.body.style.zoom='{x}%'")

    def pageBack(self):
        self.browserWebDriver.back()
        self.wait_till_loaded()

    def wait_to_login(self, user_xpath, pswd_xpath, username, password, target_url, max_login_attempts=5):
        self.login(user_xpath, pswd_xpath, username, password, target_url)
        # login_attempts = 0

        # while login_attempts < max_login_attempts:
        #     try:
        #         Log.info(f"Waiting for user (you) to login to {target_url}")
        #         login(user_xpath, pswd_xpath, username, password, target_url)
        #         break
        #     except:
        #         login_attempts += 1
        #         if login_attempts == max_login_attempts:
        #             Log.info(f"Max login attempts ({max_login_attempts}) reached. Giving up on logging in.")
        #             # Handle the case where login fails for the maximum number of attempts
        #             break
        #         Log.info(f"Login attempt {login_attempts} failed. Retrying...")
        #         continue

    def login(self, user_xpath, pswd_xpath, login_button_xpath, username, password, target_url):
        Log.info('Attempting to login')
        username_field = self.find(user_xpath)
        username_field.send_keys(username)
        sleep(10)
        password_field = self.find(pswd_xpath)
        password_field.send_keys(password)
        sleep(1)
        login_button = self.find(login_button_xpath)
        login_button.click()
        sleep(3)

    def find(self, xpath):
        # Search by xpath to find the element
        try:
            elem = self.wait.until(EC.presence_of_element_located((By.XPATH, xpath)))
            return elem
        except Exception as e:
            return f'Error {e} occurred'

    def find_all(self, xpath):
        # Search by xpath to find a list of elements
        try:
            elems = self.wait.until(EC.presence_of_all_elements_located((By.XPATH, xpath)))
            return elems
        except Exception as e:
            Log.exception(f'Exception {e} occurred')
            sys.exit()

    def click(self, elem):
        # Get coords of the element
        self.wait_till_loaded()
        # click button
        try:
            self.browserWebDriver.execute_script('arguments[0].click();', elem)
        except:
            try:
                # overlapping issue, element not loaded, etc
                # click coordinates instead
                ac = ActionChains(self.browserWebDriver)
                ac.move_to_element(elem).click().perform()
            except Exception as e:
                Log.error('Unable to click element. ' + e)
