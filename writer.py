import os
from kto_me import SETTINGS_FOLDER, LOGS_FOLDER

LOLZ_LINK = "https://zelenka.guru/members/4245200/"

ALL_TXT_FILES = (
    "useless_phrases.txt",
    "kto_settings.txt",
    "db_of_nicks.txt",
    "qst_ans.txt",
)


def create_txt_files(path_to_folders=None):
    path_to_folders = path_to_folders if path_to_folders else ""

    if not os.path.exists(file := f"{path_to_folders}/{SETTINGS_FOLDER}/useless_phrases.txt"):
        with open(file, "a") as f:
            f.write(
                "пх" + "\n" + "ааа" + "\n"
            )
    if not os.path.exists(file := f"{path_to_folders}/{SETTINGS_FOLDER}/db_of_nicks.txt"):
        with open(file, "a"): pass
    if not os.path.exists(file := f"{path_to_folders}/{SETTINGS_FOLDER}/qst_ans.txt"):
        with open(file, "a") as f:
            f.write(f"Какой лолз у создателя?  |  {LOLZ_LINK}" + "\n")
    if not os.path.exists(file := f"{path_to_folders}/{SETTINGS_FOLDER}/kto_settings.txt"):
        print(
            "У вас отсутствует(или перемещен, верните его!) файл {}!\n"
            "Файл используется для установки нужных параметров, {}\n"
            "Будьте внимательны, если мы не найдем файл, "
            "то он будет автоматически создан с настройками(по умолчанию).\n"
            "P.S Вы можете вручную менять настройки(однако за работоспособность "
            "в таком случае мы не отвечаем!)\n"
            "P.P.S Вы можете менять не только файл настроек(если будете следовать "
            "структуре как в файле(структуру вы можете увидеть внутри файлов).".
            format(file[2:], "таких как установка character ai, email and password по умолчанию")
        )
        input("Если вы поняли, то просто нажмите ENTER!\n")
        with open(file, "a", encoding='utf-8') as f:
            f.write("character_ai=Gamer Boy" + "\n")
            f.write("email=None" + "\n")
            f.write("password=None" + "\n")
            f.write("auto_choice_mode=False" + "\n")
            f.write("if_auto_choice_on_to_choose_the_mode=2" + "\n")
            f.write("nick_of_bot_creator=@xpearhead" + "\n")
            f.write("save_logs=True" + "\n")
            f.write("quantity_of_msgs=6" + "\n")
            f.write("redirecting=False" + "\n")
            f.write("quantity_of_messages_for_redirecting=10" + "\n")
            f.write(
                "message=Извини, мне надо срочно идти, напиши, плиз, свой тг, там пообщаемся(если хочешь)" + "\n"
            )
            f.write("my_gender=М" + "\n")
            f.write("partners_gender=Ж" + "\n")
            f.write("my_age=12345" + "\n")
            f.write("partners_age=12345" + "\n")
            f.write("hide=False" + "\n")
            f.write("if_ask_tg=False" + "\n")
            f.write("my_tg=None" + "\n")


def create_folders(path_to_folders=None):
    path_to_folders = path_to_folders if path_to_folders else ""

    if not os.path.isdir(path := f'{path_to_folders}/{LOGS_FOLDER}'):
        os.mkdir(path)

    if not os.path.isdir(path := f'{path_to_folders}/{SETTINGS_FOLDER}'):
        os.mkdir(path)
