from pydantic import BaseModel, validator


class Phone(BaseModel):
    phone_num: str | None = None
    country: str | None = None
    region: str | None = None

    @validator('phone_num')
    def parse_phone(cls, value: str):
        value = value.strip().replace(' ', '').replace('-', '')
        value = "+" + value if value[0] != "+" and len(value) >= 11 else value
        return value

    @property
    def country_code(self):
        return self.phone_num[1:-10] if len(self.phone_num) >= 12 else None

    @property
    def operator_code(self):
        return self.phone_num[1:-7][-3:] if len(self.phone_num) >= 12 else None

    @property
    def number(self):
        return self.phone_num[-7:] if len(self.phone_num) >= 12 else None

    def __str__(self):
        if self.country_code is not None:
            return f"Телефон: {self.phone_num}\nСтрана: Name({self.country_code})\n" \
               f"Принадлежность к региону: Region({self.operator_code})\nКороткий номер: {self.number}"
        else:
            return f"Телефон: {self.phone_num}"

phon = 79141111111
ph = Phone(phone_num=phon)
print(f"Input: {phon}")
print(ph)
