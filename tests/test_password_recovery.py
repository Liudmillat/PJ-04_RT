import pytest
from selenium import webdriver
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from settings import (valid_email, valid_password, new_password, unregistered_email)


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


# RT-008: Восстановление пароля через email
def test_password_recovery(driver):
    # Выбрать 'Забыл пароль'
    driver.find_element(By.ID, "forgot_password").click()

    # Выбрать таб 'Почта'
    driver.find_element(By.ID, "t-btn-tab-mail").click()

    #  В поле 'Почта' вводим актуальный email
    driver.find_element(By.ID, "username").send_keys(valid_email)

    time.sleep(30)
    # Вводим капчу вручную

    # Нажать 'Продолжить'
    driver.find_element(By.ID, "reset").click()

    # Ожидаем поле для ввода кода из email
    WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.ID, "rt-code-0"))
    )
    time.sleep(30)
    # Ввести код из письма вручную

    # Ввести новый пароль в основное поле и поле повторения
    driver.find_element(By.ID, "password-new").send_keys(new_password)
    driver.find_element(By.ID, "password-confirm").send_keys(new_password)

    # Нажать Подтвердить
    driver.find_element(By.ID, "t-btn-reset-pass").click()

    # Ожидаем перехода на страницу авторизации
    WebDriverWait(driver, 10).until(
        EC.url_contains("/auth/realms/b2c/login-actions/authenticate")
    )
    assert "login" in driver.current_url


# RT-009: Проверка валидации нового пароля
def test_password_validation(driver):
    # Выбрать 'Забыл пароль'
    driver.find_element(By.ID, "forgot_password").click()

    # Выбрать таб 'Почта'
    driver.find_element(By.ID, "t-btn-tab-mail").click()

    # В поле 'Почта' вводим актуальный email
    driver.find_element(By.ID, "username").send_keys(valid_email)

    time.sleep(30)
    # Вводим капчу вручную

    # Нажать 'Продолжить'
    driver.find_element(By.ID, "reset").click()

    # Ожидаем поле для ввода кода из email
    WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.ID, "rt-code-0"))
    )
    time.sleep(40)
    # Ввести код из письма вручную

    # Ожидаем поле для пароля
    WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.ID, "password-new"))
    )

    # Вводим невалидный пароль
    invalid_passwords = [
        "кириллица",  # Только кириллицей
        "short11",  # Короткий
        "nocaps123"  # Без заглавных букв
    ]

    for pwd in invalid_passwords:
        new_pass = driver.find_element(By.ID, "password-new")
        new_pass.clear()
        new_pass.send_keys(pwd)

        # Клик по полю 'Подтверждение пароля'
        driver.find_element(By.ID, "password-confirm").click()

        # Проверяем сообщения об ошибках
        error_message = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.ID, "password-new-meta"))
        )
        assert "Пароль должен содержать" or "Длина пароля должна быть" in error_message.text


#  RT-010: Невозможность восстановления пароля для незарегистрированного email
def test_recovery_unregistered_email(driver):
    # Выбираем 'Забыл пароль'
    driver.find_element(By.ID, "forgot_password").click()

    # Выбираем таб 'Почта'
    driver.find_element(By.ID, "t-btn-tab-mail").click()

    # Вводим незарегистрированный email
    driver.find_element(By.ID, "username").send_keys(unregistered_email)

    time.sleep(30)
    # Вводим капчу вручную

    # Нажать 'Продолжить'
    driver.find_element(By.ID, "reset").click()

    # Проверяем сообщение об ошибке
    error_message = WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.ID, "form-error-message"))
    )
    assert "Неверный логин или текст с картинки" in error_message.text


# RT-011: Проверка истории паролей
def test_password_history(driver):
    # Выбрать 'Забыл пароль'
    driver.find_element(By.ID, "forgot_password").click()

    # Выбрать таб 'Почта'
    driver.find_element(By.ID, "t-btn-tab-mail").click()

    #  В поле 'Почта' вводим актуальный email
    driver.find_element(By.ID, "username").send_keys(valid_email)

    time.sleep(30)
    # Вводим капчу вручную

    # Нажать 'Продолжить'
    driver.find_element(By.ID, "reset").click()

    # Ожидаем поле для ввода кода из email
    WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.ID, "rt-code-0"))
    )
    time.sleep(30)
    # Ввести код из письма вручную

    # Ввести предыдущий пароль в основное поле, перейти к полю подтверждения
    driver.find_element(By.ID, "password-new").send_keys(valid_password)
    driver.find_element(By.ID, "password-confirm").click()

    # Проверяем сообщение об ошибке
    error_message = WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located(By.ID, "")
    )
    assert "Этот пароль уже использовался" in error_message.text
