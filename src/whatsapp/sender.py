from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import time
import os

class WhatsAppSender:
    def __init__(self):
        self.driver = None

    def start_driver(self):
        options = webdriver.ChromeOptions()
        options.add_argument("--start-maximized")
        self.driver = webdriver.Chrome(options=options)
        self.driver.get("https://web.whatsapp.com")
        print("Please scan the QR code to login...")
        
        # Wait for the login to complete
        WebDriverWait(self.driver, 60).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '[data-testid="chat-list"]'))
        )

    def send_message(self, number, message, media_path=None):
        if not self.driver:
            self.start_driver()

        try:
            # Format the URL with the phone number
            url = f"https://web.whatsapp.com/send?phone={number}"
            self.driver.get(url)

            # Wait for the chat to load
            chat_box = WebDriverWait(self.driver, 20).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, '[data-testid="conversation-compose-box-input"]'))
            )

            # Send media if provided
            if media_path and os.path.exists(media_path):
                attach_button = self.driver.find_element(By.CSS_SELECTOR, '[data-testid="attach-clip"]')
                attach_button.click()
                
                # Find and click the image input
                image_input = self.driver.find_element(By.CSS_SELECTOR, 'input[type="file"]')
                image_input.send_keys(media_path)
                
                # Wait for media to upload
                time.sleep(2)

            # Type and send message
            chat_box.send_keys(message)
            chat_box.send_keys(Keys.ENTER)

            # Wait for message to be sent
            time.sleep(2)

        except Exception as e:
            print(f"Error sending message to {number}: {str(e)}")

    def send_bulk_messages(self, numbers, message, media_path=None):
        for number in numbers:
            self.send_message(number, message, media_path)

    def quit(self):
        if self.driver:
            self.driver.quit()
