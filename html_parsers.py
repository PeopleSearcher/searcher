from bs4 import BeautifulSoup as bs


def parse_html_saverudata(divs: [str]):
    persons = []
    for div in divs:
        person = {}
        div = f"""<html><body>{div}</body></html>"""
        soup = bs(div, features="html.parser")
        phone = soup.find("b", string="Телефон:")
        person["phone"] = f"{phone.nextSibling}"
        spans = soup.findAll('span')
        prev_span = ""
        for span in spans:
            try:
                prev_span = span['title']
                if span.nextSibling.text == "ID профиля Facebook:":
                    value = f"{span.nextSibling.nextSibling.nextSibling.next_element.text}\n"
                else:
                    value = f"{span.nextSibling.nextSibling}\n"
                if prev_span in person.keys():
                    if f"{span.nextSibling.text}" in person[prev_span].keys():
                        person[prev_span][f"{span.nextSibling.text}"] = person[prev_span][f"{span.nextSibling.text}"] + \
                                                                    value
                    else:
                        person[prev_span][f"{span.nextSibling.text}"] = value
                else:
                    person[prev_span] = {f"{span.nextSibling.text}": value}
            except KeyError:
                if "additional" in person.keys():
                    person["additional"] = person["additional"] + f"*{span.text} - {span.nextSibling} {span.nextSibling.nextSibling.nextSibling}\n"
                else:
                    person[
                        "additional"] = f"*{span.text} - {span.nextSibling} {span.nextSibling.nextSibling.nextSibling}\n"
        print(person)
