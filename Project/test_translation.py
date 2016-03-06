import unittest
from yandex_translate import YandexTranslate, YandexTranslateException
import yandex
import os

YANDEX_API_KEY=os.environ.get("YANDEX_API_KEY")

class YandexTranslateTest(unittest.TestCase):

    def setUp(self):
        self.translate = YandexTranslate(YANDEX_API_KEY)
    
    def test_langs(self):
        languages = self.translate.langs
        self.assertEqual(languages, set(
          [
            u"el", u"en", u"ca", u"it",
            u"hy", u"cs", u"et", u"az",
            u"es", u"ru", u"nl", u"pt",
            u"no", u"tr", u"lv", u"lt",
            u"ro", u"pl", u"be", u"fr",
            u"bg", u"hr", u"de", u"da",
            u"fi", u"hu", u"sr", u"sq",
            u"sv", u"mk", u"sk", u"uk",
            u"sl"
          ]
    ))

    def test_lang_detection(self):
        language = self.translate.detect("Je m'appele Malika")
        self.assertEqual(language, 'fr')

    def test_translation(self):
        result = self.translate.translate(u"Hello", 'en-es')
        self.assertEqual(result["text"][0], u"Hola")
        self.assertEqual(result["code"], 200)

    def test_opposite_translation(self):
        result = self.translate.translate(u"Hola", 'es-en')
        self.assertEqual(result["text"][0], u"Hello")
        self.assertEqual(result["code"], 200)


if __name__ == "__main__":
  unittest.main()