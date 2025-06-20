import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from settings import (valid_phone, valid_email, valid_password, valid_login,
                      valid_account, invalid_account, invalid_password)
import time


# Фикстура для инициализации и закрытия браузера
@pytest.fixture(autouse=True)
def driver():
    driver = webdriver.Chrome()
    driver.implicitly_wait(10)
    driver.maximize_window()
    # Переходим на страницу авторизации
    driver.get('https://b2c.passport.rt.ru/')

    yield driver

    driver.quit()


# RT-001: Успешная авторизация по номеру телефона
def test_succesful_phone_auth(driver):
    phone_field = driver.find_element(By.ID, "username")
    phone_field.send_keys(valid_phone)

    password_field = driver.find_element(By.ID, "password")
    password_field.send_keys(valid_password)

    login_button = driver.find_element(By.ID, "kc-login")
    login_button.click()

    WebDriverWait(driver, 10).until(
        EC.url_contains("account_b2c/page")
    )
    assert "account_b2c/page" in driver.current_url


# RT-002: Невозможность авторизации с неверным паролем
def test_invalid_password_auth(driver):
    phone_field = driver.find_element(By.ID, "username")
    phone_field.send_keys(valid_phone)

    password_field = driver.find_element(By.ID, "password")
    password_field.send_keys(invalid_password)

    time.sleep(20)
    # Ввести капчу вручную

    login_button = driver.find_element(By.ID, "kc-login")
    login_button.click()

    error_message = WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.ID, "form-error-message"))
    )
    forgot_password = driver.find_element(By.ID, "forgot_password")
    time.sleep(10)
    assert "Неверный логин или пароль" in error_message.text
    assert "rt-link--orange" in forgot_password.get_attribute("class")


# RT-003: Успешная авторизация по email
def test_succesful_email_auth(driver):
    email_field = driver.find_element(By.ID, "username")
    email_field.send_keys(valid_email)

    password_field = driver.find_element(By.ID, "password")
    password_field.send_keys(valid_password)

    time.sleep(30)
    # Ввести капчу вручную

    login_button = driver.find_element(By.ID, "kc-login")
    login_button.click()

    WebDriverWait(driver, 10).until(
        EC.url_contains("account_b2c/page")
    )
    time.sleep(10)
    assert "account_b2c/page" in driver.current_url


# RT-004: Успешная авторизация по логину
def test_succesful_login_auth(driver):
    login_field = driver.find_element(By.ID, "username")
    login_field.send_keys(valid_login)

    password_field = driver.find_element(By.ID, "password")
    password_field.send_keys(valid_password)

    login_button = driver.find_element(By.ID, "kc-login")
    login_button.click()

    WebDriverWait(driver, 10).until(
        EC.url_contains("account_b2c/page")
    )
    assert "account_b2c/page" in driver.current_url


# RT-005: Успешная авторизация по лицевому счёту
def test_succesful_account_auth(driver):
    account_field = driver.find_element(By.ID, "username")
    account_field.send_keys(valid_account)

    password_field = driver.find_element(By.ID, "password")
    password_field.send_keys(valid_password)

    login_button = driver.find_element(By.ID, "kc-login")
    login_button.click()

    WebDriverWait(driver, 10).until(
        EC.url_contains("account_b2c/page")
    )
    assert "account_b2c/page" in driver.current_url


# RT-006: Невозможность авторизации по несуществующему лицевому счёту
def test_invalid_account_auth(driver):
    account_field = driver.find_element(By.ID, "username")
    account_field.send_keys(invalid_account)

    password_field = driver.find_element(By.ID, "password")
    password_field.send_keys(valid_password)

    login_button = driver.find_element(By.ID, "kc-login")
    login_button.click()

    error_message = WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.ID, "form-error-message"))
    )
    forgot_password = driver.find_element(By.ID, "forgot_password")
    time.sleep(10)
    assert "Неверный логин или пароль" in error_message.text
    assert "rt-link--orange" in forgot_password.get_attribute("class")


# RT-007: Автоматическое переключение таба при вводе email
def test_auto_switch_to_email_tab(driver):
    phone_tab = driver.find_element(By.ID, "t-btn-tab-phone")
    assert "rt-tab--active" in phone_tab.get_attribute("class")

    phone_field = driver.find_element(By.ID, "username")
    phone_field.send_keys(valid_email)

    driver.implicitly_wait(10)
    password_field = driver.find_element(By.ID, "password")
    password_field.click()

    email_tab = driver.find_element(By.ID, "t-btn-tab-mail")
    assert "rt-tab--active" in email_tab.get_attribute("class")
