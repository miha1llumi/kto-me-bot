from typing import Union

from writer import (SETTINGS_FOLDER, change_settings, create_folders,
                    create_txt_files)

# предварительное создание папок
# если таковых не имеется
create_folders()
# создание файлов для настроек
create_txt_files()


class SettingVarUnFoundError(Exception):
    """
    Имя переменной в файле для настроек не была найдено
    """


class FileDataChecker:
    def __set_name__(self, class_owner, name):
        setattr(class_owner, name, self.find_value_for_attr(name, class_owner))

    def find_value_for_attr(self, name, class_owner):
        key, value = change_settings(name)
        if value:
            value = self.validate_value(key, value, class_owner)
            return value
        raise SettingVarUnFoundError(f"В файле настроек отсутствует необходимая переменная {name}")

    @staticmethod
    def validate_value(key, value, class_owner):
        annotation = class_owner.__annotations__[key]
        if annotation is str:
            return value
        if annotation is int:
            return int(value)
        if annotation is bool:
            return True if value == "True" else False
        if annotation is Union[None, str]:
            return None if value == "None" else value


class AllFilesVars:
    AI_NAME: str = FileDataChecker()
    EMAIL: Union[None, str] = FileDataChecker()
    PASSWORD: Union[None, str] = FileDataChecker()
    AUTO_CHOICE_MODE: bool = FileDataChecker()
    CHOOSE_THE_MODE: str = FileDataChecker()
    NICK_OF_BOT_CREATOR: str = FileDataChecker()
    SAVE_LOGS: bool = FileDataChecker()
    QUANTITY_OF_MESSAGES_TO_SAVE: int = FileDataChecker()
    REDIRECTING: bool = FileDataChecker()
    LAST_MESSAGE: str = FileDataChecker()
    QUANTITY_OF_MESSAGES_REDIRECTING: int = FileDataChecker()
    MY_GENDER: str = FileDataChecker()
    PARTNERS_AGE: str = FileDataChecker()
    MY_AGE: str = FileDataChecker()
    PARTNERS_GENDER: str = FileDataChecker()
    HIDE_BROWSER: bool = FileDataChecker()
    ASKING_TG: bool = FileDataChecker()
    MY_TG: str = FileDataChecker()
