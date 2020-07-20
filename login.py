from selenium import webdriver


class Login:


    def __init__(self, lang):
        self.BASE_URL = "https://" + lang + ".forgeofempires.com/glps/iframe-login"


    def login(self, username, password):
        driver = webdriver.Chrome()

        driver.get(self.BASE_URL)
        driver.find_element_by_id('login_userid').send_keys(username)
        driver.find_element_by_id('login_password').send_keys(password)
        driver.find_element_by_id('login_Login').click()

        print(driver.get_cookies())

        driver.quit()
