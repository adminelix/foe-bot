import base64
import json
import re
import time

import brotli
import psutil
import requests
from browsermobproxy import Server
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from bmp_loader import BmpLoader


class Login:
    def __init__(self, lang, world):
        self.BASE_URL = "https://" + lang + ".forgeofempires.com/glps/iframe-login"
        self.WORLD = world
        BmpLoader().prepare()

    def login(self, username, password):
        print('logging in')

        for proc in psutil.process_iter():
            # check whether the process name matches
            if proc.name() == "browsermob-proxy":
                proc.kill()

        # https://stackoverflow.com/questions/48201944/how-to-use-browsermob-with-python-selenium

        server = Server(path="./browsermob-proxy/bin/browsermob-proxy", options={'port': 8090})
        server.start()
        time.sleep(1)
        proxy = server.create_proxy()
        time.sleep(1)

        options = Options()
        options.add_argument("--headless")
        options.add_argument('--ignore-certificate-errors')
        capabilities = options.to_capabilities()
        proxy.add_to_webdriver_capabilities(capabilities)
        driver = webdriver.Firefox(desired_capabilities=capabilities)

        proxy.new_har("inno", options={'captureHeaders': True, 'captureContent': True, 'captureBinaryContent': True})

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
                if self.WORLD == element.get_attribute('value'):
                    element.click()
                    break

            while not driver.get_cookie('instanceId'):
                print('waiting for instanceId')
                time.sleep(1)

            cookies = driver.get_cookies()
            driver.quit()
        except Exception as ex:
            print('could not login')
            raise ex
        finally:
            server.stop()
            driver.quit()

        return self.__create_session(cookies, proxy)

    def __create_session(self, cookies, proxy):
        filtered_log_entries = self.__filter_log_entries(proxy)
        client_id = self.__get_client_id(filtered_log_entries[-1])
        headers = self.__get_headers(filtered_log_entries)
        contents = self.__get_contents(filtered_log_entries)
        request_id = self.__get_current_request_id(contents)
        cookies.append({'domain': 'local', 'name': 'clientId', 'path': '/', 'secure': True, 'value': client_id})
        cookies.append({'domain': 'local', 'name': 'request_id', 'path': '/', 'secure': True, 'value': request_id})

        r = requests.Session()
        for cookie in cookies:
            r.cookies.set(cookie['name'], cookie['value'], path=cookie['path'], domain=cookie['domain'])
        for header in headers:
            r.headers.setdefault(header['name'], header['value'])
        r.headers.update({'User-Agent': i['value'] for i in headers if i['name'] == 'User-Agent'})
        print('successfully logged in to world ' + self.WORLD + ' with client id: ' + client_id)
        return r, contents

    @staticmethod
    def __get_headers(filtered_log_entries):
        headers = filtered_log_entries[-1]['request']['headers']
        res = [i for i in headers if not (i['name'] == 'Host')
               and not (i['name'] == 'Content-Length')
               and not (i['name'] == 'Origin')
               and not (i['name'] == 'Referer')
               and not (i['name'] == 'Cookie')
               and not (i['name'] == 'Signature')]
        return res

    @staticmethod
    def __get_client_id(log_entry):
        client_id = [query_param for query_param in log_entry['request']['queryString']
                     if re.match("h", query_param['name'])]

        return client_id[0]['value']

    @staticmethod
    def __filter_log_entries(proxy):
        filtered_log_entries = []
        while not filtered_log_entries:
            log_entries = proxy.har['log']['entries']
            filtered_log_entries = [foo for foo in log_entries
                                    if re.match(".+/game/json\?h=.+", foo['request']['url'])]
            time.sleep(1)
        return filtered_log_entries

    @staticmethod
    def __get_contents(log_entries):
        contents = []
        for log in log_entries:
            content = json.loads(brotli.decompress(base64.b64decode(log['response']['content']['text'])))
            [contents.append(item) for item in content]
        return contents

    @staticmethod
    def __get_current_request_id(contents):
        request_id = 0
        for content in contents:
            request_id = content['requestId'] > request_id and content['requestId'] or request_id
        return request_id
