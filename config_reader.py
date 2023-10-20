SETTINGS_FOLDER = "settings"

# set up the variables from kto_settings.txt
for text in open(f"{SETTINGS_FOLDER}/kto_settings.txt", encoding='utf-8').readlines():
    try:
        key, value = text.strip().split("=")
    except ValueError:
        raise ValueError("Пожалуйста, соблюдайте структуру, не забывайте ставить '='!")
    if key == "character_ai":
        AI_NAME = value
    if key == "email":
        EMAIL = None if value == "None" else value
    if key == "password":
        PASSWORD = None if value == "None" else value
    if key == "auto_choice_mode":
        AUTO_CHOICE_MODE = True if value == "True" else False
    if key == "if_auto_choice_on_to_choose_the_mode":
        CHOOSE_THE_MODE = value
    if key == "nick_of_bot_creator":
        NICK_OF_BOT_CREATOR = value
    if key == "save_logs":
        SAVE_LOGS = True if value == "True" else False
    if key == "quantity_of_msgs":
        NECESSARY_QUANTITY_MESSAGES_TO_SAVE = int(value)
    if key == "redirecting":
        REDIRECTING = True if value == "True" else False
    if key == "message":
        LAST_MESSAGE = value
    if key == "quantity_of_messages_for_redirecting":
        MESSAGES_FOR_REDIRECTING = int(value)
    if key == "my_gender":
        MY_GENDER = value
    if key == "partners_gender":
        PARTNERS_GENDER = value
    if key == "my_age":
        MY_AGE = value
    if key == "partners_age":
        PARTNERS_AGE = value
    if key == "hide":
        HIDE_BROWSER = True if value == "True" else False
    if key == "if_ask_tg":
        ASK_TG = True if value == "True" else False
    if key == "my_tg":
        MY_TG = value
