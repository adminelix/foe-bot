from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException


class Login:
    def __init__(self, lang):
        self.BASE_URL = "https://" + lang + ".forgeofempires.com/glps/iframe-login"

    def login(self, username, password):
        driver = webdriver.Chrome()

        try:
            driver.get(self.BASE_URL)
            driver.find_element_by_id('login_userid').send_keys(username)
            driver.find_element_by_id('login_password').send_keys(password)
            driver.find_element_by_id('login_Login').click()

            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, 'play_now_button')))

            result = driver.get_cookies()
            print('successfully logged in')
        except TimeoutException:
            print('could not login')
            raise
        finally:
            driver.quit()

        return result
