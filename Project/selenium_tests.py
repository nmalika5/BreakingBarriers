import unittest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
import time

class TestAppSignUp(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        cls.driver = webdriver.Chrome('/Users/malikanikhmonova/Downloads/chromedriver')
        cls.driver.get("http://localhost:5000")

    @classmethod
    def tearDownClass(cls):
        cls.driver.quit()
        
    def test_home_title(self):
        self.assertEqual(self.driver.title, 'LingoChat')

    def test_signup(self):
        signup = self.driver.find_element_by_link_text('Signup')
        signup.click()
        email = self.driver.find_element_by_name('email')
        email.send_keys("automated@test.com")
        password = self.driver.find_element_by_name('password')
        password.send_keys("test5")
        fname = self.driver.find_element_by_name('first_name')
        fname.send_keys("Automated")
        lname = self.driver.find_element_by_name('last_name')
        lname.send_keys("Test")
        lang = Select(self.driver.find_element_by_name('lang_id'))
        lang.select_by_visible_text('Afrikaans')
        phone = self.driver.find_element_by_name('phone')
        phone.send_keys("4153417706")
        self.driver.find_element_by_id("submit").click()
        self.assertEqual(self.driver.title, u'LingoChat')

    def test_user_login(self):
        self.driver.find_element_by_link_text('LingoChat').click()
        username = self.driver.find_element_by_name('email')
        username.send_keys("demo@email.com")
        password = self.driver.find_element_by_name('password')
        password.send_keys("test")
        self.driver.find_element_by_id("submit").click()
        self.assertEqual(self.driver.title, u'LingoChat')


    def test_user_message(self):
        textarea = self.driver.find_element_by_id('message')
        textarea.send_keys("hi")
        contact = self.driver.find_element_by_id("49")
        contact.click()
        preview = self.driver.find_element_by_id("preview")
        preview.click()
        result = self.driver.find_element_by_id("results")
        self.assertTrue(result)
        send = self.driver.find_element_by_id("send")
        send.click()


if __name__ == '__main__':
    unittest.main()