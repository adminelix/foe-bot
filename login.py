from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from browsermobproxy import Server
import psutil
import time
import re


class Login:
    def __init__(self, lang, world):
        self.BASE_URL = "https://" + lang + ".forgeofempires.com/glps/iframe-login"
        self.WORLD = world

    def login(self, username, password):

        for proc in psutil.process_iter():
            # check whether the process name matches
            if proc.name() == "browsermob-prox":
                proc.kill()

        # https://stackoverflow.com/questions/48201944/how-to-use-browsermob-with-python-selenium

        dict = {'port': 8090}
        server = Server(path="./browsermob-proxy/bin/browsermob-proxy", options=dict)
        server.start()
        time.sleep(1)
        proxy = server.create_proxy()
        time.sleep(1)

        chrome_options = Options()
        # chrome_options.add_argument("--headless")
        chrome_options.add_argument('--ignore-certificate-errors')
        capabilities = chrome_options.to_capabilities()
        proxy.add_to_webdriver_capabilities(capabilities)
        driver = webdriver.Chrome(desired_capabilities=capabilities)

        proxy.new_har("inno")

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
            elements = driver.find_elements_by_class_name(
                'world_select_button')

            for element in elements:
                print(element.get_attribute('value'))
                if self.WORLD == element.get_attribute('value'):
                    element.click()
                    break

            result = driver.get_cookies()
            print('successfully logged in')
            client_id = self.__get_client_id(proxy)
            result.append(client_id)

        except Exception as ex:
            print('could not login')
            raise ex
        finally:
            server.stop()
            driver.quit()

        return result

    @classmethod
    def __get_client_id(cls, proxy):
        filtered_log_entries = []
        while not filtered_log_entries:
            log_entries = proxy.har['log']['entries']
            filtered_log_entries = [foo for foo in log_entries
                if re.match(".+/game/json\?h=.+", foo['request']['url'])]
            time.sleep(1)

        first = filtered_log_entries[0]
        client_id = [query_param for query_param in first['request']['queryString']
               if re.match("h", query_param['name'])]

        return client_id
