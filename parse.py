from bs4 import BeautifulSoup


def find_values_by_parse(name, attrs, driver, all_values=True, params=None):
    soup = BeautifulSoup(driver.page_source, "html.parser")
    values = soup.find_all(name, attrs) if all_values else soup.find(*params)
    return values


def retrieve_ai_message(text, driver):
    return find_values_by_parse("div", {"class": "swiper-no-swiping"}, driver)[-1].text.split("☆")[0]


def find_new_messages(who_is, driver):
    return find_values_by_parse("div", {"class": f"mess_block {who_is} window_chat_dialog_new"}, driver)
