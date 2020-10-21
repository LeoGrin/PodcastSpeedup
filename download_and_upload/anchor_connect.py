from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import selenium
import time
from selenium.webdriver.support.wait import WebDriverWait
import os.path



def upload_podcast(audio_filepath, image_filepath, name, description, login, password):
    """
    Upload the podcast episode to Anchor through Selenium
    :param filepath: filepath of the audio file to upload
    :param name: Name of the podcast (to appear to listener)
    :param description: Description of the podcast (to appear to listener)
    :param login:  Login to connect to Anchor
    :param password: Password to connect to Anchor
    :return: True if the upload was successful, False otherwise
    """
    #TODO make headless to speed up
    start_time = time.time()
    print("Connecting to anchor....")
    login_url = "https://anchor.fm/login"
    driver = webdriver.Firefox()
    driver.maximize_window()
    driver.get(login_url)
    elem_email = driver.find_element_by_xpath('//*[@id="email"]')
    elem_email.send_keys(login)
    elem_password = driver.find_element_by_xpath('//*[@id="password"]')
    elem_password.send_keys(password)
    button_login = driver.find_element_by_xpath('//*[@id="LoginForm"]/div[3]/button')
    button_login.click()
    time.sleep(10)
    wait = WebDriverWait(driver, 20)
    button_new_episode = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="app"]/div/nav/div/div/div/div[1]/div[2]/a/div/div/div/button/div/div/div')))
    button_new_episode.click()
    print("Uploading episode...")
    button_upload = wait.until(EC.presence_of_element_located((By.XPATH, '/html/body/div/div/div[1]/div/div/div/div/div[2]/div[1]/div[1]/div/input')))
    button_upload.send_keys(os.path.abspath(audio_filepath)) #selenium needs the absolute file path
    time.sleep(1)
    wait = WebDriverWait(driver, 5000)
    button_save = wait.until(EC.element_to_be_clickable((By.XPATH, '/html/body/div/div/div[1]/div/div/div/div/div[2]/button')))
    button_save.click()
    wait = WebDriverWait(driver, 50)
    elem_title = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="title"]')))
    time.sleep(1)
    elem_description = driver.find_element_by_xpath('/html/body/div/div/div[1]/div/div/form/div[1]/div[2]/div[2]/div/label/div[2]/div/div/div[2]/div/div[2]/div')
    elem_title.send_keys(name)
    time.sleep(2)
    elem_description.send_keys(description)
    time.sleep(1)
    if image_filepath:
        button_image = driver.find_element_by_xpath('/html/body/div/div/div/div/div/form/div[3]/div[2]/div[1]/div/div/input')
        button_image.send_keys(os.path.abspath(image_filepath))
        time.sleep(2)
        wait = WebDriverWait(driver, 10)
        button_save_image = wait.until(EC.presence_of_element_located((By.XPATH, '/html/body/div[2]/div[2]/div/div/div[2]/p/button[1]')))
        button_save_image.click()
    time.sleep(3)
    publish_button = driver.find_element_by_xpath('/html/body/div/div/div[1]/div/div/form/div[1]/div[1]/div[2]/div[2]/div/div/div/button/div/div/div')
    publish_button.click()
    wait = WebDriverWait(driver, 200)
    print("It took {} seconds".format(int(time.time() - start_time)))
    try:
        wait.until(EC.presence_of_element_located((By.XPATH, '/html/body/div/div/div[1]/div/div/div/div[1]')))
        print("Successful upload !")
        driver.close()
        return True
    except selenium.common.exceptions.TimeoutException:
        print("Error, the podcast may not be uploaded...")
        driver.close()
        return False



if __name__ == """__main__""":
    login_url = "https://anchor.fm/login"
    login = "leo.grinsztajn@gmail.com"
    password = "7Nathanleomax61"
    print(os.getcwd())
    #filepath = "/Users/anne/PycharmProjects/podcast-app/audio-files/wiblin-trimmed.mp3"
    audio_filepath = "audio-files/silence.wav"
    image_filepath = "temp_folder/image.jpg"
    episode_name = "Wiblin episode trimmed"
    episode_description = "This is a test !"
    upload_podcast(audio_filepath, image_filepath, episode_name, episode_description, login, password)