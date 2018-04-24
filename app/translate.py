import requests
import json
from flask import current_app


def translation(text, source_lang, dest_lang):
    """Use Microsoft translation service to translate texts"""

    if 'MS_TRANSLATION_KEY' not in current_app.config or \
            not current_app.config['MS_TRANSLATION_KEY']:
        return 'Translation key has not been set up.'
    auth = {'Ocp-Apim-Subscription-Key':
            current_app.config['MS_TRANSLATION_KEY']}

    r = requests.get('https://api.microsofttranslator.com/v2/Ajax.svc'
                     '/Translate?text={}&from={}&to={}'.
                     format(text, source_lang, dest_lang), headers=auth)
    if r.status_code != 200:
        return 'Oops, the translation service failed.'

    return json.loads(r.content.decode('utf-8-sig'))
