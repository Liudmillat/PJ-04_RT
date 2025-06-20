import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from settings import (valid_email)
import time
from faker import Faker

fake = Faker('ru_RU')


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


# RT-012: Успешная регистрация нового пользователя с помощью email/телефона
def test_succesful_registration(driver):
    #  Переходим на страницу регистрации
    driver.find_element(By.ID, "kc-register").click()

    # Заполняем данные
    first_name = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.NAME, "firstName"))
     )
    first_name.send_keys(fake.first_name())

    last_name = driver.find_element(By.NAME, "lastName")
    last_name.send_keys(fake.last_name())

    region = driver.find_element(
        By.XPATH, "//input[@class='rt-input__input rt-select__input rt-input__input--rounded rt-input__input--orange']"
    )
    region.send_keys("Москва")
    driver.find_element(By.XPATH, "//div[@class='rt-select__list-wrapper rt-select__list-wrapper--rounded']").click()

    # Генерируем уникальный email
    email = f'test_{fake.user_name()}@example.com'
    email_input = driver.find_element(By.ID, "address")
    email_input.send_keys(email)

    # Создаем валидный пароль
    password = "ValidTestPass789"
    password_input = driver.find_element(By.ID, "password")
    password_input.send_keys(password)

    password_confirm = driver.find_element(By.ID, "password-confirm")
    password_confirm.send_keys(password)

    # Нажать 'Зарегистрироваться'
    driver.find_element(By.NAME, "register").click()

    time.sleep(30)
    # Вводим капчу вручную

    # Нажать 'Продолжить'
    driver.find_element(By.XPATH, "//button[@class='rt-btn rt-btn--orange rt-btn--medium rt-btn--rounded']").click()

    # Ожидаем поле для ввода кода из email
    WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.ID, "rt-code-0"))
    )
    time.sleep(30)
    # Ввести код из письма вручную

    # Проверяем успешную регистрацию
    WebDriverWait(driver, 10).until(
        EC.url_contains("account_b2c/page")
    )
    assert "account_b2c/page" in driver.current_url


# RT-013: Невозможность регистрации с уже существующим email
def test_registration_with_existing_email(driver):

    #  Переходим на страницу регистрации
    driver.find_element(By.ID, "kc-register").click()

    # Вводим уже зарегистрированный email
    email_input = driver.find_element(By.ID, "address")
    email_input.send_keys(valid_email)

    # Заполняем другие обязательные поля
    first_name = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.NAME, "firstName"))
    )
    first_name.send_keys(fake.first_name())

    last_name = driver.find_element(By.NAME, "lastName")
    last_name.send_keys(fake.last_name())

    region = driver.find_element(
        By.XPATH, "//input[@class='rt-input__input rt-select__input rt-input__input--rounded rt-input__input--orange']"
    )
    region.send_keys("Москва")
    driver.find_element(By.XPATH, "//div[@class='rt-select__list-wrapper rt-select__list-wrapper--rounded']").click()

    # Создаем валидный пароль
    password = "ValidTestPass789"
    password_input = driver.find_element(By.ID, "password")
    password_input.send_keys(password)

    password_confirm = driver.find_element(By.ID, "password-confirm")
    password_confirm.send_keys(password)

    # Нажать 'Зарегистрироваться'
    driver.find_element(By.NAME, "register").click()

    # Ожидаем сообщение об ошибке
    error_message = WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.CLASS_NAME, "card-modal__title"))
    )
    assert "Учётная запись уже существует" in error_message.text


# RT-014: Невозможность регистрации с невалидными данными
def test_invalid_registration_data(driver):

    #  Переходим на страницу регистрации
    driver.find_element(By.ID, "kc-register").click()

    # Заполняем поля невалидными данными
    driver.find_element(By.NAME, "firstName").send_keys("A")
    driver.find_element(By.NAME, "lastName").send_keys("Б")
    driver.find_element(By.ID, "address").send_keys("invalid-email")
    driver.find_element(By.ID, "password").send_keys("пароль1")
    driver.find_element(By.ID, "password-confirm").send_keys("другойпароль")

    # Нажать 'Зарегистрироваться'
    driver.find_element(By.NAME, "register").click()

    # Ожидаем ошибки
    wait = WebDriverWait(driver, 10)

    # Проверка сообщений об ошибках
    # Имя
    first_name_error = wait.until(
        EC.visibility_of_element_located((By.XPATH, "//*[@id='page-right']/div/div[1]/div/form/div[1]/div[1]/span"))
    )
    assert "Необходимо заполнить поле кириллицей. От 2 до 30 символов." in first_name_error.text

    # Фамилия
    last_name_error = wait.until(
        EC.visibility_of_element_located((By.XPATH, "//*[@id='page-right']/div/div[1]/div/form/div[1]/div[2]/span"))
    )
    assert "Необходимо заполнить поле кириллицей. От 2 до 30 символов." in last_name_error.text

    # Email
    email_error = wait.until(
        EC.visibility_of_element_located((By.XPATH, "//*[@id='page-right']/div/div[1]/div/form/div[3]/div/span"))
    )
    assert "Введите телефон в формате" in email_error.text or "email в формате" in email_error.text

    # Пароль
    password_error = wait.until(
        EC.visibility_of_element_located((By.XPATH, "//*[@id='page-right']/div/div[1]/div/form/div[4]/div[1]/span"))
    )
    assert "Пароль должен содержать" in password_error.text or "Длина пароля должна быть не менее 8 символов" in password_error.text

    # Подтверждение пароля
    driver.find_element(By.ID, "password").clear()
    driver.find_element(By.ID, "password").send_keys("Pass1234")
    driver.find_element(By.ID, "password-confirm").clear()
    driver.find_element(By.ID, "password-confirm").send_keys("Pass4321")

    confirm_password_error = wait.until(
        EC.visibility_of_element_located((By.XPATH, "//*[@id='page-right']/div/div[1]/div/form/div[4]/div[2]/span"))
    )
    assert "Пароли не совпадают" in confirm_password_error.text
