import json
import unittest

from models.data import Phone


class PhoneTests(unittest.TestCase):
    def full_test(self):
        phone_num = 79142900258
        expected = {"phone_num": "+79142900258", "country": "Россия", "region": "Республика Саха-Якутия", "operator": "MTC"}
        phone = Phone(phone_num=phone_num)

        self.assertEqual(expected, json.loads(phone.json()))

    def test_formatting(self):
        phone_num = '+7 (914) 290-02-58'
        expected = {"phone_num": "+79142900258", "country": "Россия", "region": "Республика Саха-Якутия",
                    "operator": "MTC"}
        phone = Phone(phone_num=phone_num)

        self.assertEqual(expected, json.loads(phone.json()))


if __name__ == '__main__':
    unittest.main()
