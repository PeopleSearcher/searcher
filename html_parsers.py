from bs4 import BeautifulSoup as bs
from bs4.element import Tag, NavigableString


def parse_html_saverudata(divs: [str]):
    persons = []
    for div in divs:
        person = {}
        div = f"""<html><body>{div}</body></html>"""
        soup = bs(div, features="html.parser")
        phone = soup.find("b", string="Телефон:")
        person["phone"] = f"{phone.nextSibling}"
        cur_elem = phone.nextSibling.nextSibling
        # move down per line
        while cur_elem.text != "полное досье":
            if type(cur_elem) == Tag:
                if cur_elem.name == "br":
                    cur_elem = cur_elem.nextSibling
                    pass  # skip br tag
                elif cur_elem.name == 'span':
                    value = ""
                    cur_val = cur_elem.nextSibling
                    key = ""
                    # move right per elem in string
                    while True:
                        if type(cur_val) == Tag and cur_val.name == 'br':
                            if type(cur_val.nextSibling) == NavigableString:
                                value += f"{cur_val.nextSibling} "
                            else:
                                if cur_elem['title'] in person.keys():
                                    if key in person[cur_elem['title']].keys():
                                        person[cur_elem['title']][key] = person[cur_elem['title']][key] + value + "\n"
                                    else:
                                        person[cur_elem['title']][key] = value + "\n"
                                else:
                                    person[cur_elem['title']] = {f"{key}": value+'\n'}
                                cur_elem = cur_val.nextSibling
                                break
                        elif type(cur_val) == Tag and cur_val.name == "b":
                            key = cur_val.text.strip()
                        elif type(cur_val) == NavigableString:
                            if key == "":
                                key = "IP"
                                value = cur_val.strip().split(":")[1]
                            else:
                                value += f"{cur_val.strip()} "
                        elif type(cur_val) == Tag and (cur_val.name == "span" or cur_val.name == "a"):
                            value += f"{cur_val.text.strip()} "

                        cur_val = cur_val.nextSibling
        persons.append(person)
    return persons
