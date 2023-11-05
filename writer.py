import os

from kto_me import LOGS_FOLDER, SETTINGS_FOLDER

LOLZ_LINK = "https://zelenka.guru/members/4245200/"

ALL_TXT_FILES = (
    "useless_phrases.txt",
    "kto_settings.txt",
    "db_of_nicks.txt",
    "qst_ans.txt",
)


def create_txt_files(path_to_folders=None):
    path_to_folders = os.getcwd() + (path_to_folders if path_to_folders else "")
    common_path = f"{path_to_folders}/{SETTINGS_FOLDER}"

    if not os.path.exists(file_path := f"{common_path}/useless_phrases.txt"):
        with open(file_path, "a") as f:
            f.write(
                "пх" + "\n" + "ааа" + "\n"
            )
    if not os.path.exists(file_path := f"{common_path}/db_of_nicks.txt"):
        with open(file_path, "a"): pass
    if not os.path.exists(file_path := f"{common_path}/qst_ans.txt"):
        with open(file_path, "a") as f:
            f.write(f"Какой лолз у создателя?  |  {LOLZ_LINK}" + "\n")
    if not os.path.exists(file_path := f"{common_path}/kto_settings.txt"):
        print(
            "У вас отсутствует(или перемещен, верните его!) файл {}!\n"
            "Файл используется для установки нужных параметров, {}\n"
            "Будьте внимательны, если мы не найдем файл, "
            "то он будет автоматически создан с настройками(по умолчанию).\n"
            "P.S Вы можете вручную менять настройки(однако за работоспособность "
            "в таком случае мы не отвечаем!)\n"
            "P.P.S Вы можете менять не только файл настроек(если будете следовать "
            "структуре как в файле(структуру вы можете увидеть внутри файлов).".
            format(file_path[2:], "таких как установка character ai, email and password по умолчанию")
        )
        input("Если вы поняли, то просто нажмите ENTER!\n")
        with open(file_path, "a", encoding='utf-8') as f:
            f.write("AI_NAME=Gamer Boy" + "\n")
            f.write("EMAIL=None" + "\n")
            f.write("PASSWORD=None" + "\n")
            f.write("AUTO_CHOICE_MODE=False" + "\n")
            f.write("CHOOSE_THE_MODE=2" + "\n")
            f.write("NICK_OF_BOT_CREATOR=@xpearhead" + "\n")
            f.write("SAVE_LOGS=True" + "\n")
            f.write("QUANTITY_OF_MESSAGES_TO_SAVE=6" + "\n")
            f.write("REDIRECTING=False" + "\n")
            f.write("QUANTITY_OF_MESSAGES_REDIRECTING=10" + "\n")
            f.write(
                "LAST_MESSAGE=Извини, мне надо срочно идти, напиши, плиз, "
                "свой тг, там пообщаемся(если хочешь)" + "\n"
            )
            f.write("MY_GENDER=М" + "\n")
            f.write("PARTNERS_GENDER=Ж" + "\n")
            f.write("MY_AGE=2" + "\n")
            f.write("PARTNERS_AGE=12345" + "\n")
            f.write("HIDE_BROWSER=False" + "\n")
            f.write("ASKING_TG=False" + "\n")
            f.write("MY_TG=None" + "\n")


def create_folders(path_to_folders=None):
    path_to_folders = os.getcwd() + (path_to_folders if path_to_folders else "")

    if not os.path.isdir(path := f'{path_to_folders}/{LOGS_FOLDER}'):
        os.mkdir(path)

    if not os.path.isdir(path := f'{path_to_folders}/{SETTINGS_FOLDER}'):
        os.mkdir(path)


def change_settings(searching_name=None):
    settings = {}
    for text in open(file_path := f"{os.getcwd()}/{SETTINGS_FOLDER}/kto_settings.txt", encoding='utf-8').readlines():
        text = text.strip()
        try:
            key, value = text.split("=")
        except ValueError:
            raise ValueError("Не забывайте '=' после названия элемента настройки!")
        # если поисковое имя для поиска не задано или не найдено
        # то функция вернет None
        if searching_name is None:
            change = input(
                f"Значение {key} сейчас = {value}\n"
                f"Вы хотите поменять значение? [Y/N(press ENTER)]: "
            )
            if change == "Y":
                value = input("Введите новое значение: ")
        else:
            if key == searching_name:
                return key, value
        settings[key] = value
    # удаляем прошлый файл
    os.remove(f"{os.getcwd()}/{file_path}")
    # записать значения
    with open(file_path, "a", encoding='utf-8') as file:
        for k, vl in settings.items():
            file.write(f"{k}={vl}" + "\n")


def exist_qst_in_bd(question):
    if not isinstance(question, str):
        return False

    with open(f"{SETTINGS_FOLDER}/qst_ans.txt", "r") as _f:
        for qst in _f.readlines():
            if question.upper() == (qst := qst.split("|"))[0].upper():
                return qst[-1]


def write_dialog(answers):
    with open(f"{SETTINGS_FOLDER}/qst_ans.txt", "a") as _f:
        for qst, ans in answers.items():
            if not exist_qst_in_bd(qst):
                _f.write(f"{qst}  |  {ans}" + "\n")
