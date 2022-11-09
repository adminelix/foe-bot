import json
import logging
import os
import re
import time

import requests
from selenium.common.exceptions import  TimeoutException
from selenium.webdriver import DesiredCapabilities
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from urllib import parse
import undetected_chromedriver as webdriver

from foe_bot.exceptions import WrongCredentialsException, WorldNotFoundException
from foe_bot.util import foe_json_loads


class Login:
    def __init__(self, lang, world):
        self.__logger = logging.getLogger(self.__class__.__name__)
        self.BASE_URL = "https://" + lang + ".forgeofempires.com/glps/iframe-login"
        self.WORLD = world
        self.retries = 0

    def login(self, username, password):
        self.__logger.info(f"logging into world {self.WORLD} with user {username}")

        options = Options()
        options.headless = False
        options.add_argument('--no-sandbox')
        capabilities = DesiredCapabilities.CHROME
        capabilities["goog:loggingPrefs"] = {"performance": "ALL"}
        driver = webdriver.Chrome(options=options, desired_capabilities=capabilities)
        # blocks creation of websocket that would increase the request counter
        driver.rewrite_rules = [(r'.*/socket/$', 'https://localhost:9876/')]

        try:
            driver.get(self.BASE_URL)
            driver.find_element(By.ID, 'login_userid').send_keys(username)
            driver.find_element(By.ID, 'login_password').send_keys(password)
            driver.find_element(By.ID, 'login_Login').click()

            try:
                WebDriverWait(driver, 2).until(
                    EC.presence_of_element_located((By.CLASS_NAME, 'validation-message-error')))
                raise WrongCredentialsException("wrong credentials provided")
            except TimeoutException:
                pass

            WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.ID, 'play_now_button'))).click()
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, 'world_select_button')))
            elements = driver.find_elements(By.CLASS_NAME, 'world_select_button')

            for element in elements:
                if self.WORLD == element.get_attribute('value'):
                    if not element.is_displayed():
                        raise WorldNotFoundException('no city found for given world')
                    element.click()
                    break
            self.__logger.info(f"successfully logged into world {self.WORLD} - waiting for token")

            reqs = self.__wait_until_loaded_and_get_requests(driver)
            signature_key = self.__extract_signature_key(reqs)
            filtered_reqs = self.__filter_requests(reqs)

            for req in filtered_reqs:
                try:
                    req['message']['message']['params']['response'] = driver.execute_cdp_cmd('Network.getResponseBody', {'requestId': req["message"]["message"]["params"]["requestId"]})
                except Exception:
                    continue

            game_vars = driver.execute_script('return gameVars')
            cookies = driver.get_cookies()
            cookies.append({'domain': 'local', 'name': 'socketGatewayUrl',
                            'path': '/', 'secure': True, 'value': game_vars['socketGatewayUrl']})
            cookies.append({'domain': 'local', 'name': 'socket_token',
                            'path': '/', 'secure': True, 'value': game_vars['socket_token']})

            self.retries = 0
            self.__logger.info("got token")

        except (WrongCredentialsException, WorldNotFoundException) as ex:
            driver.save_screenshot(f"{os.path.dirname(os.path.realpath(__file__))}/../../data/error_screenshot.png")
            raise ex
        except Exception as ex:
            driver.save_screenshot(f"{os.path.dirname(os.path.realpath(__file__))}/../../data/error_screenshot.png")
            self.__logger.error(f"could not login, retry {self.retries}", ex)
            self.retries += 1
            if self.retries < 3:
                return self.login(username, password)
            raise ex
        finally:
            driver.quit()

        return self.__create_session(cookies, filtered_reqs, signature_key)

    def __wait_until_loaded_and_get_requests(self, driver):
        reqs: list = list()
        timeout = time.time() + 40

        while not self.__is_loaded(reqs):
            if time.time() > timeout:
                raise TimeoutError("waiting for token timed out")

            reqs.extend([log for log in driver.get_log("performance")])
            time.sleep(0.2)

        for req in reqs:
            req['message'] = json.loads(req['message'])

        return reqs

    def __create_session(self, cookies, reqs, signature_key):
        client_id = self.__get_client_id(reqs)
        headers = self.__get_headers(reqs)
        contents = self.__get_contents(reqs)
        request_id = self.__get_current_request_id(contents)
        cookies.append({'domain': 'local', 'name': 'clientId',
                        'path': '/', 'secure': True, 'value': client_id})
        cookies.append({'domain': 'local', 'name': 'request_id',
                        'path': '/', 'secure': True, 'value': request_id})
        cookies.append({'domain': 'local', 'name': 'signature_key',
                        'path': '/', 'secure': True, 'value': signature_key})

        session = requests.Session()
        for cookie in cookies:
            session.cookies.set(cookie['name'], cookie['value'],
                                path=cookie['path'], domain=cookie['domain'])
        for header in headers:
            session.headers.setdefault(header[0], header[1])
        session.headers.update(
            {'User-Agent': header[1] for header in headers if header[0] == 'user-agent'})

        self.__logger.info(f"successfully logged in to world {self.WORLD} with client id {client_id}")
        return session, contents

    @staticmethod
    def __get_client_id(reqs) -> str:
        url = reqs[-1]['message']['message']['params']['request']['url']
        query_params = parse.parse_qs(parse.urlsplit(url).query)
        return query_params['h'][0]

    @staticmethod
    def __is_loaded(reqs) -> bool:
        return True if [req for req in reqs if
                        re.match(r".+/game/json\?h=.+", req['message'])
                        and re.match(r".+LoadTimePerformance.+", req['message'])] \
            else False

    @staticmethod
    def __get_headers(reqs):
        headers = reqs[-1]['message']['message']['params']['request']['headers']
        excludes = ['Host', 'content-length', 'origin', 'referer', 'cookie', 'signature']
        res = dict(filter(lambda val: val[0] not in excludes, headers.items()))
        return res

    @staticmethod
    def __filter_requests(reqs):
        re_filter = r".+/game/json\?h=.+"
        filtered: list = list()

        for req in reqs:
            try:
                if re.match(re_filter, req['message']['message']['params']['request']['url']):
                    filtered.append(req)
            except KeyError:
                continue

        return filtered

    @staticmethod
    def __get_contents(reqs):
        contents: list = list()
        for req in reqs:
                content = foe_json_loads(req['message']['message']['params']['response']['body'])
                [contents.append(item) for item in content]
        return contents

    @staticmethod
    def __get_current_request_id(contents):
        req_id = 0
        for content in contents:
            req_id = content.get('requestId', -1) > req_id and content['requestId'] or req_id
        return req_id

    @staticmethod
    def __extract_signature_key(reqs):
        re_filter = r'.+foede\.innogamescdn\.com\/cache\/Forge.+\.js'
        re_extract = r'(?<=encode\(this\._signatureHash\+")(.*)(?="\+)'

        url: str = ""
        for req in reqs:
            try:
                if re.match(re_filter, req['message']['message']['params']['request']['url']):
                    url = req['message']['message']['params']['request']['url']
            except KeyError:
                continue

        if not url:
            raise KeyError("no url")

        response = requests.get(url)
        body = response.content.decode('utf-8')
        return re.findall(re_extract, body)[0]
