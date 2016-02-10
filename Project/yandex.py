from yandex_translate import YandexTranslate

api_key = 'trnsl.1.1.20160208T195023Z.302d7000bf527427.e55e9fa77c97a0706b125efc605e8e90a40f20cb'
translate = YandexTranslate(api_key)
print('Languages:', translate.langs)
print('Translate directions:', translate.directions)
print('Detect language:', translate.detect('Hello, world!'))
print('Translate:', translate.translate('Hello, world!', 'en-fr'))


message_text = "hello world"
from_lang = "en"
to_lang = "fr"
    
def translate(message_text, from_lang, to_lang):
    """Translates a message"""

    lang_combo = from_lang + "-" + to_lang

    return translate(message_text, lang_combo)
    

# text = 'Hello'
# source="en"
# target="ru"
 
# obj = translate(api_key, text, target, source)

# def print_emp(api, emp_id):
#     """Print detail about an employee."""

#     print
#     print label
#     print

#     emp = requests.get(
#         "http://localhost:5000/%s/employee/%s" % (api, emp_id)).json()
#     pprint(emp, width=40, indent=2)

#     print
#     raw_input("=====")

#     def translate(text, from_lang, to_lang):
#         """Translates the text from one lang to another"""

#         url = "https://translate.yandex.net/api/v1.5/tr.json/translate?hl=%s&sl=%s&q=%s" % ()

#         request = requests.get

# payload = {'term': 'watermelon'}
# r = requests.get("https://translate.yandex.net/api/v1.5/tr.json/translate?", params=payload)

# melon_songs = r.json()

# num_results = melon_songs['resultCount']

# for i in range(num_results):
#     trackName = melon_songs['results'][i].get('trackName')
#     artistName = melon_songs['results'][i].get('artistName')
#     print "%s : %s" % (trackName, artistName)


