import unittest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

class TestChat(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        cls.driver = webdriver.Chrome('/Users/malikanikhmonova/Downloads/chromedriver')
        cls.driver.set_window_size(1240,500)
        cls.driver.get("http://localhost:5000")

    @classmethod
    def tearDownClass(cls):
        cls.driver.quit()

    def test_home_title(self):
        self.assertEqual(self.driver.title, 'LingoChat')

    def test_login(self):
        username = self.driver.find_element_by_name('email')
        username.send_keys("message@test.com")
        password = self.driver.find_element_by_name('password')
        password.send_keys("test")
        self.driver.find_element_by_id("submit").click()
        self.assertEqual(self.driver.title, u'My App')

    def test_send_message(self):
        textarea = self.driver.find_element_by_id('message')
        textarea.send_keys("hi")
        contact = self.driver.find_element_by_id("49")
        contact.click()
        preview = self.driver.find_element_by_id("preview")
        preview.click()
        result = self.driver.find_element_by_id("results")
        self.assertTrue(result)
        # send = self.driver.find_element_by_id("send")
        # send.click()

    # def test_signup(self):
    #     self.driver.get("http://localhost:5000")
    #     self.driver.get('/register')
    #     email = self.driver.find_element_by_name('email')
    #     email.send_keys("automated@test.com")
    #     password = self.driver.find_element_by_name('password')
    #     password.send_keys("test")
    #     fname = self.driver.find_element_by_name('first_name')
    #     lname = self.driver.find_element_by_name('last_name')
    #     lang = self.driver.find_element_by_name('lang_id')
    #     phone = self.driver.find_element_by_name('phone')
    #     self.driver.find_element_by_id("submit").click()
    #     self.assertEqual(self.driver.title, u'My App')



if __name__ == '__main__':
    unittest.main()