from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException


class Login:
    def __init__(self, lang, world):
        self.BASE_URL = "https://" + lang + ".forgeofempires.com/glps/iframe-login"
        self.WORLD = world

    def login(self, username, password):
        driver = webdriver.Chrome()

        try:
            driver.get(self.BASE_URL)
            driver.find_element_by_id('login_userid').send_keys(username)
            driver.find_element_by_id('login_password').send_keys(password)
            driver.find_element_by_id('login_Login').click()

            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, 'play_now_button')))
            driver.find_element_by_id('play_now_button').click()

            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, 'world_select_button')))
            elements = driver.find_elements_by_class_name('world_select_button')

            for element in elements:
                print(element.get_attribute('value'))
                if self.WORLD == element.get_attribute('value'):
                    element.click()
                    break

            result = driver.get_cookies()
            print('successfully logged in')
        except TimeoutException:
            print('could not login')
            raise
        finally:
            # driver.quit()
            pass

        return result
