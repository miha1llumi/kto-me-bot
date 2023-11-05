# kto_me v1.0.5
import os
from datetime import datetime, timedelta
from string import ascii_letters, digits
from time import sleep

import pyperclip
from chromedriver_py import binary_path
from fake_useragent import UserAgent
from selenium import webdriver
from selenium.common.exceptions import (ElementClickInterceptedException,
                                        ElementNotInteractableException,
                                        InvalidSessionIdException,
                                        NoSuchElementException,
                                        NoSuchWindowException,
                                        StaleElementReferenceException,
                                        TimeoutException,
                                        UnexpectedAlertPresentException,
                                        WebDriverException)
from selenium.webdriver import ActionChains
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium_recaptcha_solver import RecaptchaException, RecaptchaSolver

from parse import find_new_messages, find_values_by_parse, retrieve_ai_message
from selector import SELECTORS

if __name__ == "__main__":
    from config_reader import AllFilesVars
    from writer import (change_settings, create_folders, create_txt_files,
                        exist_qst_in_bd, write_dialog)

LOLZ_LINK = "https://zelenka.guru/members/4245200/"
GITHUB_LINK = "https://github.com/miha1llumi"

SETTINGS_FOLDER = "settings"
LOGS_FOLDER = "logs"


def set_drivers_settings():
    user_agent = UserAgent()
    user_agent = user_agent.random
    options = Options()
    if AllFilesVars.HIDE_BROWSER:
        options.add_argument("--headless")
    options.add_argument('log-level=3')
    options.add_argument("--start-maximized")
    options.add_argument(f"user-agent={user_agent}")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("detach", True)
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)
    try:
        serv = Service(executable_path=binary_path)
    except WebDriverException:
        raise FileExistsError("Установите google chrome browser на ваш компьютер.")
    drv = webdriver.Chrome(service=serv, options=options)
    return drv


def ignor_exceptions(func, ignored_exceptions, is_exit=False, **params):
    while True:
        try:
            return func(**params)
        except ignored_exceptions:
            if is_exit:
                return


def go_to_site(*, link, load_time, one_time=True):
    # окно по какому-то странному образу вызывает ошибку
    # так как оно закрыто, но мы пытаемся что-то сделать
    ignor_exceptions(
        func=driver.execute_script,
        is_exit=True,
        ignored_exceptions=(NoSuchWindowException, InvalidSessionIdException),
        script=f'''window.open("{link}", "_blank");'''
    )
    sleep(load_time)
    driver.switch_to.window(window_name=driver.window_handles[0])
    if one_time:
        driver.close()
    driver.switch_to.window(window_name=driver.window_handles[0 if one_time else -1])


def set_up_settings_for_webdriver():
    while True:
        global driver, solver
        driver = set_drivers_settings()
        # решатель капч
        solver = RecaptchaSolver(driver=driver)
        go_to_site(link="https://nekto.me/chat/", load_time=9)
        if find_values_by_parse("h2", {"id": "challenge-running"}, driver):
            driver.close()
        else:
            break
    return driver, solver


def press_enter_by_driver():
    ActionChains(driver) \
        .send_keys(Keys.ENTER) \
        .perform()


def is_captcha():
    try:
        sleep(1)
        driver.find_element(By.XPATH, '//iframe[@title="reCAPTCHA"]').click()
    except (ElementNotInteractableException, NoSuchElementException,
            ElementNotInteractableException, ElementClickInterceptedException):
        return False
    else:
        driver.refresh()
        return True


def clean_text_from_extra_characters(msg, clean_time=True):
    if not msg:
        return None
    # максимально можно убрать только 4 цифры
    # так как время состоит из 4 цифр
    figures_for_cleaning = 4
    quantity_of_figures = 0
    rvs_msg = msg[::-1]
    if clean_time:
        while True:
            if not rvs_msg:
                return None
            char = rvs_msg[0]
            if char in digits:
                quantity_of_figures += 1
            if quantity_of_figures <= figures_for_cleaning:
                # если это так, значит это возраст
                rvs_msg = rvs_msg[1:]
                # если мы очистили от времени(4 цифры)
                if quantity_of_figures == 4:
                    break
    rvs_msg = rvs_msg[::-1]
    # иногда боты отправляют текст с пометкой того
    # что они боты, так что убираем ее
    if '-'.join(part for part in AllFilesVars.AI_NAME.split()) in rvs_msg and ":" in rvs_msg:
        while rvs_msg[0] != ":":
            rvs_msg = rvs_msg[1:]
        # чтобы избавиться от ":"
        rvs_msg = rvs_msg[1:]
    return rvs_msg


def try_to_solve_captcha():
    try:
        sleep(1)
        recaptcha_iframe = driver.find_element(By.XPATH, '//iframe[@title="reCAPTCHA"]')
        solver.click_recaptcha_v2(iframe=recaptcha_iframe)
    except RecaptchaException:
        driver.refresh()
        time_to_wait = 15
        print(
            f"Мы вынуждены перезагрузить страницу.\n"
            f"Бот не может решить капчу(гугл засек автоматизированные запросы)\n"
            f"Можете решить капчу самостоятельно или подождите({time_to_wait}с)."
        )
        sleep(time_to_wait)
    except (NoSuchElementException, ElementClickInterceptedException):
        driver.refresh()
    except TimeoutException:
        pass
    else:
        print("Бот решил капчу, наслаждайтесь")


def copy_text(answer, clean_time=True):
    try:
        pyperclip.copy(
            clean_text_from_extra_characters(
                answer,
                clean_time=clean_time,
            )
        )
    except pyperclip.PyperclipException:
        pyperclip.copy("Эх(")
        print(
            "Во время копирования произошла ошибка."
            "Скорее всего, это произошло из-за использования "
            "двух одинаковых веб драйверов одновременно\n"
            "Или вы пользовались компьютером параллельно с программой\n"
            "Поэтому мы заменили это на 'Эx('"
        )


def wait_the_solution():
    while is_captcha():
        try_to_solve_captcha()


def start_chat_to_ai(is_acception=True):
    def fill_in_the_form():
        def enter_em_and_pas():
            __email = input("email: ")
            __password = input("password: ")
            return __email, __password

        def find_the_user_element():
            try:
                return driver.find_element(By.ID, "username")
            except NoSuchElementException:
                sleep(1)
            finally:
                return driver.find_element(By.ID, "username")

        def clean_inputs():
            try:
                user_el = find_the_user_element()
                user_el.click()
                for char in range(50):
                    user_el.send_keys(Keys.ARROW_RIGHT)
                    user_el.send_keys(Keys.BACKSPACE)
            except ElementClickInterceptedException:
                # пользователь до сих пор не прошел капчу
                return False
            else:
                return True

        if not (AllFilesVars.EMAIL and AllFilesVars.PASSWORD):
            print("Введите данные(email или username) для сайта character ai(предварительно зарегистрируйтесь)")
        email_and_pass = all(_ for _ in (AllFilesVars.EMAIL, AllFilesVars.PASSWORD))
        email, password = AllFilesVars.EMAIL, AllFilesVars.PASSWORD if email_and_pass else enter_em_and_pas()

        # если находит, то ошибка character ai
        if find_values_by_parse("div", {"class": "error-header"}, driver):
            driver.refresh()

        while True:
            sleep(1)
            # если возникла такая ошибка, значит пользователь сам проходит капчу
            ignor_exceptions(
                func=try_to_solve_captcha,
                is_exit=True,
                ignored_exceptions=(StaleElementReferenceException,)
            )
            # при обновлении страницы остается старый email
            # так что мы стираем все символы
            while not clean_inputs(): pass

            username = find_the_user_element()
            username.click()
            username.send_keys(email)
            _password = driver.find_element(By.ID, "password")
            _password.click()
            _password.send_keys(password)

            # confirm form
            try:
                driver. \
                    find_element(By.XPATH, SELECTORS['XPATH_LOGIN_FORM_CONFIRM(format1)'].format("")). \
                    click()
            except NoSuchElementException:
                driver. \
                    find_element(By.XPATH, SELECTORS['XPATH_LOGIN_FORM_CONFIRM(format1)'].format("[1]")). \
                    click()
            except ElementClickInterceptedException:
                # пользователь в это время сам вводит капчу
                pass

            sleep(1)
            if "Welcome" not in driver.page_source:
                break

            if "Wrong email" in driver.page_source:
                print(
                    "\033[31m {}\033[0m".
                    format(
                        "Wrong email or password!\n"
                        " Please enter email and password again."
                    )
                )
                email, password = enter_em_and_pas()
            # при обновлении страницы остается старый email
            # так что мы стираем все символы
            while not clean_inputs(): pass

    def find_the_character_ai():
        driver.get("https://beta.character.ai/search?")
        sleep(1.5)
        try:
            search_inp = driver. \
                find_element(By.ID, "search-input")
        except NoSuchElementException:
            driver.refresh()
            sleep(3)
            search_inp = driver. \
                find_element(By.ID, "search-input")
        search_inp.click()
        search_inp.send_keys(
            AllFilesVars.AI_NAME + Keys.SPACE + AllFilesVars.NICK_OF_BOT_CREATOR
        )
        # чтобы раскрыть панель со списком ai
        press_enter_by_driver()
        sleep(2)
        # значит списка ai нет совсем
        if not find_values_by_parse("div", {"class": "character-row"}, driver):
            print(
                "Поиск не находит ai. Мы вынуждены убрать ник автора!"
            )
            for _ in AllFilesVars.NICK_OF_BOT_CREATOR:
                search_inp.send_keys(Keys.BACKSPACE)
            press_enter_by_driver()
            sleep(2)
        # choice character
        driver.find_element(By.CSS_SELECTOR, SELECTORS['CSS_AI_DIV']).click()
        sleep(2)
        request_for_ai("Привет", wait_answer=False)
        # переключение на другое окно
        driver.switch_to.window(window_name=driver.window_handles[0])
        sleep(1)

    sleep(2)
    if is_acception:
        # accept something
        driver. \
            find_element(By.CSS_SELECTOR, r"#\#AcceptButton").click()
        # go to log in
        driver. \
            find_element(By.CSS_SELECTOR, SELECTORS['CSS_LOG_IN_BUTTON']).click()
        # wait for the downloading page
        sleep(1)

        fill_in_the_form()
    find_the_character_ai()


def request_for_ai(sentence, wait_answer=True):
    def find_ai_msgs():
        return find_values_by_parse("div", {"class": "swiper-no-swiping"}, driver)

    try:
        # вводим текст, который собеседник написал нам
        user_input = driver. \
            find_element(By.ID, "user-input")
        user_input.click()
        copy_text(
            sentence,
            clean_time=False
        )
        user_input.send_keys(
            Keys.CONTROL + "v" + Keys.ENTER
        )
    except NoSuchElementException:
        # сайт завис, selenium не может найти элементы
        # ничего не делаем, так как ниже перезаход на сайт
        pass
    # проверка на гостя в character ai, иногда бывает баг
    # что ai отображается в гостевом режиме, перезаходим
    if find_values_by_parse("span", {"class": "msg-author-name"}, driver):
        print(
            "К сожалению, на сайте произошел баг\n"
            "Мы вынуждены перезайти на сайт."
        )
        driver.close()
        go_to_character_ai()
        return

    if wait_answer:
        try:
            fake_typing(time=3.8)
        except RuntimeError:
            # пользователь завершил чат
            return
        ai_msgs = find_ai_msgs()
        # проверка на отправку сообщения от бота
        while len(ai_msgs) != len(find_ai_msgs()):
            sleep(1)
            ai_msgs = find_ai_msgs()
        try:
            last_ai_msg = ai_msgs[-1].text.split("☆")[0]
        except IndexError:
            # страница не загружается, проблема с сайтом
            # надо войти заново
            print(
                "Произошла ошибка в работе сайта character_ai!\n"
                "Мы вынуждены прервать диалог и перезайти."
            )
            # возвращение в главное меню
            driver.execute_script("window.history.go(-2)")
            start_chat_to_ai(is_acception=False)
            return
        # сравниваем изменилось ли за время кол-во символов
        # если да, то ai еще формулирует свою мысль
        sleep(1)
        new_last_ai_msg = retrieve_ai_message(last_ai_msg, driver)
        while len(new_last_ai_msg) > len(last_ai_msg):
            last_ai_msg = retrieve_ai_message(new_last_ai_msg, driver)
            sleep(1)
            new_last_ai_msg = retrieve_ai_message(new_last_ai_msg, driver)
        return last_ai_msg


def print_all_information():
    print(
        "Создатель: 1llumi\n"
        "lolz создателя: {}\n"
        "Гит хаб создателя: {}".
        format(LOLZ_LINK, GITHUB_LINK)
    )


def check_character_ai_cloudflare_protection():
    try:
        # если элемента нет, значит бот не прошел
        # cloudflare protection
        driver.find_element(By.ID, "header-row")
    except NoSuchElementException:
        driver.close()
        return True


def go_to_character_ai():
    def go_to_another_site():
        go_to_site(
            link="https://beta.character.ai/",
            load_time=3,
            one_time=False
        )
        return check_character_ai_cloudflare_protection()

    while True:
        try:
            while go_to_another_site(): pass
            break
        except InvalidSessionIdException:
            # все вкладки браузера были закрыты
            set_up_settings_for_webdriver()
    ignor_exceptions(
        func=start_chat_to_ai,
        ignored_exceptions=(NoSuchElementException,)
    )


def choose_mode_for_bot():
    while True:
        try:
            if not AllFilesVars.AUTO_CHOICE_MODE:
                choice_mode = input(
                    "Выбор режима:\n"
                    "1 - обучение, бот связывает слова и ответы на них для дальнейшего самостоятельного общения\n"
                    "2 - практика, бот отвечает на сообщения на основе полученных данных во время обучения и AI\n"
                    "3 - подробная информация о боте и создателе\n"
                    "4 - расширенные настройки\n"
                    "Введите цифру: "
                )
            else:
                choice_mode = AllFilesVars.CHOOSE_THE_MODE
        except NameError:
            print(
                "Проверьте правильность выставленных настроек(какая-то из них указана неверна).\n"
                "Чтобы точно избавиться от проблемы удалите файл с настройками и перезапустите скрипт."
            )
            while True: pass
        try:
            choice_mode = int(choice_mode)
        except ValueError:
            # clean console
            os.system("cls")
            print("\033[31m Введите цифру! \033[0m")
        else:
            if choice_mode == 3:
                print_all_information()
                continue
            if choice_mode == 4:
                change_settings()
                print(
                    "Чтобы изменения вошли в силу, перезапустите скрипт!"
                )
                while True: pass
            if choice_mode == 2:
                go_to_character_ai()
            if choice_mode > 4:
                print("Введите не рандомную цифру, а цифру слева от описания того, что она делает!")
                continue
            break
    return choice_mode


def start_chat_in_nekto_me(accept_rules=True):
    # нажатие на кнопку "Начать чат"
    driver.find_element(By.ID, "searchCompanyBtn").click()
    sleep(1)
    if accept_rules:
        # принять правила чата
        driver.find_element(By.CSS_SELECTOR, SELECTORS['CSS_NEKTO_ME_RULES']).click()
    print("Настройки успешно выставлены.")


def stop_searching():
    driver. \
        find_element(By.CLASS_NAME, "btn btn-lg btn-stop-search").click()


def set_up_settings():
    """
    Здесь идут общие настройки пола, возраста и т.д
    """
    # мой пол
    driver.find_element(By.CSS_SELECTOR, f"body > div.row > div > div.container.chat_container >"
                                         f" div.chat-box.col-xs-12.col-sm-12.col-md-8.col-lg-6.mainStep > div."
                                         f"row.step_chatbox.main_step > div > div.sexRow.row > div:nth-child(1) > div >"
                                         f" button:nth-child({'2' if AllFilesVars.MY_GENDER == 'М' else '3'})"
                        ).click()
    # пол собеседника
    driver.find_element(By.CSS_SELECTOR, f"body > div.row > div > div.container.chat_container > "
                                         f"div.chat-box.col-xs-12.col-sm-12.col-md-8.col-lg-6.mainStep > "
                                         f"div.row.step_chatbox.main_step > div > div.sexRow.row > "
                                         f"div.col-xs-6.col-sm-6.col-md-6.col-lg-6.wishSex.threeBtns > div "
                                         f"> button:nth-child({'3' if AllFilesVars.PARTNERS_GENDER == 'Ж' else '2'})"
                        ).click()

    def set_up_age(who_is):
        age_mode = 1 if who_is == "my" else 2
        ages = AllFilesVars.MY_AGE if who_is == "my" else AllFilesVars.PARTNERS_AGE
        for age_fig in ages:
            driver.find_element(By.CSS_SELECTOR, f"body > div.row > div > div.container.chat_container > "
                                                 f"div.chat-box.col-xs-12.col-sm-12.col-md-8.col-lg-6.mainStep > "
                                                 f"div.row.step_chatbox.main_step > div > div.row.row-search > "
                                                 f"div:nth-child({age_mode}) > div.s-age > button:nth-child({age_fig})"
                                ).click()

    set_up_age(who_is="my")
    set_up_age(who_is="partner")
    start_chat_in_nekto_me()


def wait_the_partner():
    print("Ждем собеседника...")
    try:
        time_to_reload = datetime.now() + timedelta(seconds=30)
        while "Ищем свободного собеседника..." in driver.page_source:
            sleep(1)
            now_time = datetime.now()
            if now_time > time_to_reload:
                try:
                    stop_searching()
                except NoSuchElementException:
                    # кнопка не найдена
                    # значит диалог начался
                    if not is_captcha():
                        # проверка на капчу, т.к иногда
                        # истекает время прохождения капчи
                        # бот застревает в infinity loop
                        if "Ищем свободного собеседника..." not in driver.page_source:
                            # проверяем еще раз, ибо может быть бесконечный цикл ожидания
                            return
                raise
    except UnexpectedAlertPresentException:
        # не удалось связаться с reCAPTCHA
        # пробуем пройти заново
        wait_the_solution()


def check_to_stop_to_chat():
    if is_captcha():
        return True
    return bool(
        find_values_by_parse(
            "button",
            {"class": "btn btn-md btn-my1 nst close_dialog_btn disabled"},
            driver
        )
    )


def find_next_partner():
    sleep(1)
    if element := ignor_exceptions(
            func=driver.find_element,
            is_exit=True,
            ignored_exceptions=(NoSuchElementException,),
            by=By.CSS_SELECTOR,
            value=SELECTORS['CSS_NEXT_PARTNER_BUTTON']
    ):
        try:
            element.click()
        except ElementClickInterceptedException:
            pass


def check_new_msgs(phrases, answers):
    return True if ["not empty list" for phs in phrases if phs not in answers] else False


def wait_for_the_answer_on_msgs(phrases, answers):
    for phs in phrases:
        if phs not in answers:
            _text = find_new_messages("self", driver)
            # избавляемся от None значений
            _text = [msg for msg in [clean_text_from_extra_characters(msg.text) for msg in _text] if msg]

            if ans := list(filter(lambda x: not any(x == answers.get(_ans) for _ans in answers), _text)):
                answers[phs] = ans[0]


def answer_msgs_by_myself(phrases, answers, fill_in_all_answers=False):
    for phs in phrases:
        if phs not in answers:
            text_input = driver.find_element(By.CLASS_NAME, "emojionearea-editor")
            if answer := exist_qst_in_bd(phs):
                text_input.send_keys(answer)
            elif fill_in_all_answers:
                answer = "random_answer"
            else:
                driver.switch_to.window(window_name=driver.window_handles[-1])
                request_time_start = datetime.now()
                answer = request_for_ai(phs)
                driver.switch_to.window(window_name=driver.window_handles[0])
                copy_text(
                    answer,
                    clean_time=False,
                )
                correct_typing(
                    func=text_input.send_keys,
                    keys=Keys.CONTROL + "v",
                    time=request_time_start,
                )
            try:
                text_input.send_keys(Keys.ENTER)
            except StaleElementReferenceException:
                # если элемент не найден
                press_enter_by_driver()
            answers[phs] = answer


def close_current_chat(by_myself=False):
    try:
        driver.find_element(By.CSS_SELECTOR, SELECTORS['CSS_CLOSE_DIALOG_BUTTON']).click()
        sleep(1)
        driver.find_element(By.CSS_SELECTOR, SELECTORS['CSS_CONFIRM_BUTTON_TO_CLOSE_DIALOG_WITH_PARTNER']).click()
    except:
        pass
    else:
        if not by_myself:
            print("Собеседник был неактивен в течение 30с+")


def check_unuseless_phrase(phrase):
    with open(f"{SETTINGS_FOLDER}/useless_phrases.txt", "r") as _f:
        for word in _f.readlines():
            if phrase.upper() == word.upper().strip("\n"):
                return word


def correct_typing(*, func, keys, time):
    # не считаем пробелы как за символ
    chars = len(''.join(char for char in pyperclip.paste().split()))
    while True:
        time_now = datetime.now()
        # сколько символов успел бы напечатать человек за это время
        difference_of_time = (time_now - time).seconds
        chars_of_person_for_time = difference_of_time * 5
        if chars_of_person_for_time >= chars:
            try:
                func(keys)
            except StaleElementReferenceException:
                # почему-то происходит ошибка при печати
                # возможно, такое поведение связано с using pk
                # включение/выключение монитора влияет на это(i'm not sure)
                pass
            return
        try:
            # вычисляем примерное время, сколько еще надо печатать человеку
            # чтобы он смог напечатать этот текст
            fake_typing(
                time=round(
                    (chars - chars_of_person_for_time) / 5
                ),
            )
        except RuntimeError:
            # ошибка для досрочного выхода из печати
            # т.к. собеседник завершил чат
            return
        # возвращаемся на некто ми
        driver.switch_to.window(window_name=driver.window_handles[0])


def write_the_last_message(last_message, *, answers, phrases):
    def write_in_db(_text):
        with open(f"{SETTINGS_FOLDER}/db_of_nicks.txt", "a", encoding="utf-8") as _f:
            _f.write(_text + "\n")

    nickname = ""
    another_text = ""
    text_input = driver.find_element(By.CLASS_NAME, "emojionearea-editor")
    copy_text(
        last_message,
        clean_time=False
    )
    correct_typing(
        func=text_input.send_keys,
        keys=Keys.CONTROL + "v",
        time=datetime.now(),
    )
    text_input.send_keys(Keys.ENTER)
    # находим новые сообщения
    check_and_add_partners_messages(phrases)
    # заполнить пропуски, чтобы бот на них не отвлекался
    answer_msgs_by_myself(
        answers=answers,
        phrases=phrases,
        fill_in_all_answers=True,
    )
    start_time = datetime.now()
    while True:
        partners_msgs = check_and_add_partners_messages(
            partners_phrases=phrases,
        )
        # если хотя бы один символ на английском, значит это ник
        for msg in partners_msgs:
            if msg not in answers:
                for char in msg:
                    # доступные символы для тг ника
                    if char in ascii_letters or char in digits + "_":
                        nickname += char
                    elif AllFilesVars.ASKING_TG:
                        another_text += char.upper()
        # проверка на номер телефона
        # если символов > 11, скорее всего, это номер
        if sum(_ in digits for _ in nickname) >= 11:
            write_in_db(nickname)
            break
        # иногда парсятся цифры вместе с ником
        # но тг ник не может начинаться с цифр
        try:
            while nickname[0] in digits + "_":
                nickname = nickname[1:]
        except IndexError:
            pass
        if len(nickname) >= 5:
            write_in_db(nickname)
            break
        # просят написать мой тг
        elif any(word in another_text for word in ("НАПИШИ", "СКИНЬ", "СВОЙ")):
            # если такого элемента нет, значит диалог завершен
            try:
                text_input = driver.find_element(By.CLASS_NAME, "emojionearea-editor")
                text_input.send_keys(AllFilesVars.MY_TG + Keys.ENTER)
                # для правдоподобности
                sleep(5)
            except NoSuchElementException:
                pass
            finally:
                break
        elif check_to_stop_to_chat():
            break
        else:
            now_time = datetime.now()
            if (now_time - start_time).seconds >= 90:
                break


def fake_typing(time):
    def type_and_clear(mode=None):
        for _ in range(10):
            try:
                sleep(0.04)
                text_input.send_keys(
                    "a" if mode == "type" else Keys.ARROW_RIGHT + Keys.BACKSPACE
                )
            except ElementClickInterceptedException:
                pass

    # время когда завершится печать
    time_to_over = datetime.now() + timedelta(seconds=time)
    start_time = datetime.now()
    # сохраняем окна для selenium'а
    nekto_me_window = driver.window_handles[0]
    character_ai_window = driver.window_handles[-1]
    # переходим на некто ми
    driver.switch_to.window(window_name=nekto_me_window)
    text_input = driver.find_element(By.CLASS_NAME, "emojionearea-editor")
    while start_time < time_to_over:
        try:
            type_and_clear(mode="type")
            type_and_clear(mode="clear")
        except StaleElementReferenceException:
            # элемент устарел(при взаимодействии), надо найти заново
            try:
                text_input = driver.find_element(By.CLASS_NAME, "emojionearea-editor")
            except NoSuchElementException:
                pass
        if check_to_stop_to_chat():
            raise
        start_time = datetime.now()
    # переключаемся обратно
    driver.switch_to.window(window_name=character_ai_window)


def saving_logs(title_of_folder):
    def save_screen():
        # ищем подходящее имя(по порядку)
        # для нашего скриншота
        _number = 1
        while os.path.exists(full_path := f"{os.getcwd()}/{LOGS_FOLDER}/{title_of_folder}/shot{_number}.png"):
            _number += 1
        driver.save_screenshot(full_path)
        return title_of_folder

    # если есть имя папки
    if title_of_folder:
        save_screen()
        return title_of_folder
    number = 1
    title_of_folder = f"{LOGS_FOLDER}/folder{number}"
    # ищем подходящее имя(по порядку)
    # для нашей папки
    while os.path.isdir(title_of_folder):
        number += 1
        title_of_folder = f"{LOGS_FOLDER}/folder{number}"
    os.mkdir(title_of_folder)
    save_screen()
    return title_of_folder


def clean_chat_with_ai(window_with_character_ai):
    def open_chat_settings():
        driver.find_element(By.CSS_SELECTOR, SELECTORS['CSS_SVG_WITH_CHAT_SETTINGS']).click()

    # переключаемся на окно с character ai
    driver.switch_to.window(window_name=window_with_character_ai)
    ignor_exceptions(
        func=open_chat_settings,
        is_exit=False,
        ignored_exceptions=(NoSuchElementException,),
    )
    sleep(1)
    try:
        # нажатие на save and start new chat
        driver.find_element(By.CSS_SELECTOR, SELECTORS['CSS_START_NEW_CHAT_WITH_AI_BUTTON']).click()
    except (NoSuchElementException, ElementClickInterceptedException):
        # если возникла это ошибка, значит элемент не загрузился
        # значит надо перезагрузить страницу
        driver.refresh()
    finally:
        # переключаемся на предыдущее окно
        driver.switch_to.window(window_name=driver.window_handles[0])


def print_dialog_is_over():
    print(
        "-------------------------------------------------\n"
        "Диалог завершился, если вы хотите хранить подробности переписок, \n"
        "То укажите это в расширенных настройках\n"
        "-------------------------------------------------\n"
    )


def check_and_add_partners_messages(partners_phrases):
    partners_msgs = find_new_messages("nekto", driver)
    for msg in partners_msgs:
        if _text := clean_text_from_extra_characters(msg.text):
            # проверка есть ли значение в файле фраз
            # на которые боту не надо отвечать
            if not check_unuseless_phrase(_text):
                partners_phrases.add(_text)
    return partners_phrases


def check_home_page():
    try:
        driver.find_element(By.ID, "searchCompanyBtn")
        return True
    except NoSuchElementException:
        return False


def chat_to_partner(choice_mode):
    # иногда случается, что бот думает, что диалог начался,
    # хотя он только закончился, так что делаем проверку
    print("Общение началось")
    quantity_messages_for_save_in_logs = AllFilesVars.QUANTITY_OF_MESSAGES_TO_SAVE
    folder_name_to_save_logs = None
    start_time = datetime.now()
    partners_phrases = set()
    answers = {}
    while True:
        if check_home_page():
            start_chat_in_nekto_me()
            break
        if check_to_stop_to_chat():
            print_dialog_is_over()
            if AllFilesVars.SAVE_LOGS:
                # если сообщения уже были сохранены ранее,
                # но пользователь завершил чат
                # и написал хотя бы 1 сообщение
                # все равно сохраняем переписку
                if AllFilesVars.QUANTITY_OF_MESSAGES_TO_SAVE <= len(answers.keys()) \
                        < quantity_messages_for_save_in_logs:
                    saving_logs(folder_name_to_save_logs)
            if choice_mode == 1:
                write_dialog(answers)
            if len(answers.keys()) >= 3:
                clean_chat_with_ai(
                    window_with_character_ai=driver.window_handles[-1],
                )
            find_next_partner()
            break
        check_and_add_partners_messages(partners_phrases)
        # если в настройках выставлено сохранение логов
        if AllFilesVars.SAVE_LOGS:
            if len(answers.keys()) >= quantity_messages_for_save_in_logs:
                # переменная нужна, чтобы если папка существует
                # не создавалась новая, а все сохранялось в текущую
                folder_name_to_save_logs = saving_logs(folder_name_to_save_logs)
                # увеличиваем, так как нам надо сохранить другую часть переписки
                quantity_messages_for_save_in_logs += quantity_messages_for_save_in_logs

        # перенаправление включается в настройках
        if AllFilesVars.REDIRECTING:
            if len(answers.keys()) >= AllFilesVars.QUANTITY_OF_MESSAGES_REDIRECTING:
                # бот оставляет последнее сообщение и ждет ответа, иначе переключает
                write_the_last_message(
                    AllFilesVars.LAST_MESSAGE,
                    answers=answers,
                    phrases=partners_phrases,
                )
                # на всякий случай сохраняем последний скрин
                if AllFilesVars.SAVE_LOGS:
                    try:
                        saving_logs(folder_name_to_save_logs)
                    except NameError:
                        raise "У вас нет созданной папки, укажите параметр" \
                              "quantity_of_msgs меньше чем quantity_of_messages_for_redirecting"
                # чтобы не было отправки большого кол-ва сообщений
                # как только получили ник, уходим
                clean_chat_with_ai(
                    window_with_character_ai=driver.window_handles[-1],
                )
                close_current_chat(by_myself=True)
                # break нужен за тем, чтобы чат не очищался 2 раза
                break

        if check_new_msgs(partners_phrases, answers):
            if choice_mode == 1:
                wait_for_the_answer_on_msgs(partners_phrases, answers)
            if choice_mode == 2:
                answer_msgs_by_myself(partners_phrases, answers)
            start_time = datetime.now()
        else:
            now_time = datetime.now()
            if (now_time - start_time).seconds >= 60:
                close_current_chat()


def main():
    create_folders()
    create_txt_files()
    mode = choose_mode_for_bot()
    ignor_exceptions(
        func=set_up_settings,
        ignored_exceptions=(NoSuchElementException,),
    )
    # the main logic
    while True:
        # проверка на капчу и ее решение
        wait_the_solution()
        try:
            wait_the_partner()
        except RuntimeError:
            # если возникла ошибка
            # поиск идет 30+ секунд
            start_chat_in_nekto_me(
                accept_rules=False,
            )
            continue
        chat_to_partner(choice_mode=mode)


if __name__ == "__main__":
    driver, solver = set_up_settings_for_webdriver()
    main()
