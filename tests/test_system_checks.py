import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

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


# RT-0015 Проверка отображения предупреждения при отключённых cookie
def test_cookie_warning(driver):

    # Переход на страницу
    driver.get("https://b2c.passport.rt.ru")

    # Ожидаем всплывающую подсказку
    cookie_warning = WebDriverWait(driver,10).until(
        EC.visibility_of_element_located((By.CLASS_NAME, "cookie-warning"))
    )

    # Наличие кнопки 'Повторить попытку'
    retry_button = cookie_warning.find_element(By.TAG_NAME, "button")

    assert "Cookie отключены" in cookie_warning.text
    assert "Повторить попытку" in retry_button.text


# RT-016: Корректное отображение страницы авторизации
def test_auth_page_layout(driver):

    # Проверка левой части (логотип и информация)
    left_side = WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.CSS_SELECTOR, ".what-is-container"))
    )

    logo = left_side.find_element(By.CSS_SELECTOR, ".what-is-container__logo")
    assert logo.is_displayed(), "Логотип не отображается в левой части"

    title = left_side.find_element(By.CSS_SELECTOR, ".what-is__title")
    assert "Личный кабинет" in title.text

    # Проверка правой части (форма авторизации и меню выбора типа авторизации)
    right_side = WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.CSS_SELECTOR, ".card-container__wrapper"))
    )

    # Поля формы
    username_field = right_side.find_element(By.ID, "username")
    assert username_field.is_displayed(), "Поле ввода не отображается"

    password_field = right_side.find_element(By.ID, "password")
    assert password_field.is_displayed(), "Поле пароля не отображается"

    # Меню выбора типов авторизации
    auth_tabs = right_side.find_elements(By.CSS_SELECTOR, ".rt-tab.rt-tab--small")
    assert len(auth_tabs) >= 4, "Недостаточно табов авторизации"
