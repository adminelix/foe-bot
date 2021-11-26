import json
import re
import time

import brotli
import requests
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from seleniumwire import webdriver


class Login:
    def __init__(self, lang, world):
        self.BASE_URL = "https://" + lang + ".forgeofempires.com/glps/iframe-login"
        self.WORLD = world

    def login(self, username, password):
        print('logging in')

        options = Options()
        options.add_argument("--headless")
        driver = webdriver.Firefox(options=options)

        try:
            driver.get(self.BASE_URL)
            driver.find_element_by_id('login_userid').send_keys(username)
            driver.find_element_by_id('login_password').send_keys(password)
            driver.find_element_by_id('login_Login').click()

            driver.refresh()

            WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.ID, 'play_now_button')))
            driver.find_element_by_id('play_now_button').click()

            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, 'world_select_button')))
            elements = driver.find_elements_by_class_name(
                'world_select_button')

            for element in elements:
                if self.WORLD == element.get_attribute('value'):
                    element.click()
                    break

            print('waiting for instanceId')
            while not driver.get_cookie('instanceId'):
                time.sleep(0.1)

            reqs = driver.requests
            filtered_reqs = self.__filter_requests(reqs)

            cookies = driver.get_cookies()
            driver.quit()
        except Exception as ex:
            print('could not login')
            raise ex
        finally:
            driver.quit()

        return self.__create_session(cookies, filtered_reqs)

    def __create_session(self, cookies, reqs):
        client_id = reqs[-1].params['h']
        headers = self.__get_headers(reqs)
        contents = self.__get_contents(reqs)
        request_id = self.__get_current_request_id(contents)
        cookies.append({'domain': 'local', 'name': 'clientId', 'path': '/', 'secure': True, 'value': client_id})
        cookies.append({'domain': 'local', 'name': 'request_id', 'path': '/', 'secure': True, 'value': request_id})

        session = requests.Session()
        for cookie in cookies:
            session.cookies.set(cookie['name'], cookie['value'], path=cookie['path'], domain=cookie['domain'])
        for header in headers:
            session.headers.setdefault(header[0], header[1])
        session.headers.update({'User-Agent': header[1] for header in headers if header[0] == 'user-agent'})

        print('successfully logged in to world ' + self.WORLD + ' with client id: ' + client_id)
        return session, contents

    @staticmethod
    def __get_headers(reqs):
        headers = reqs[-1].headers._headers
        res = [i for i in headers if not (i[0] == 'Host')
               and not (i[0] == 'content-length')
               and not (i[0] == 'origin')
               and not (i[0] == 'referer')
               and not (i[0] == 'cookie')
               and not (i[0] == 'signature')]
        return res

    @staticmethod
    def __filter_requests(reqs):
        filtered_reqs = []
        while not filtered_reqs:
            filtered_reqs = [req for req in reqs if re.match(".+/game/json\?h=.+", req.url)]
            time.sleep(0.1)
        return filtered_reqs

    @staticmethod
    def __get_contents(reqs):
        contents = []
        for req in reqs:
            content = json.loads(brotli.decompress(req.response.body))
            [contents.append(item) for item in content]
        return contents

    @staticmethod
    def __get_current_request_id(contents):
        req_id = 0
        for content in contents:
            req_id = content['requestId'] > req_id and content['requestId'] or req_id
        return req_id
