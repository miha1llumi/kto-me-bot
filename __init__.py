import os

# ffmpeg to complete recaptcha
try:
    import ffmpeg_downloader
except ImportError:
    os.system("pip install ffmpeg-downloader")
    os.system("ffdl install --add-path")
    print(
        "Пожалуйста, перезапустите скрипт, чтобы соответствующие изменения вступили в силу.\n"
        "Если у вас появляется надпись, что ffmpeg не найден, то это нормально, спустя время она пропадет.\n"
        "Надпись не влияет на работоспособность программы(но лучше все равно хотя бы 1 раз перезапустить скрипт).\n"
    )
    while True: pass

try:
    import selenium_recaptcha_solver
except ImportError:
    os.system("pip install selenium-recaptcha-solver")

try:
    import chromedriver_py
except ImportError:
    os.system("pip install chromedriver_py")

try:
    import fake_useragent
except ImportError:
    os.system("pip install fake-useragent")

try:
    import pyperclip
except ImportError:
    os.system("pip install pyperclip")

try:
    import bs4
except ImportError:
    os.system("pip install beautifulsoup4")
