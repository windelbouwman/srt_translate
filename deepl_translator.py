from translator_class import TranslateClass
from deepl import translator
import time


class DeeplTranslator(TranslateClass):
    retry_max = 3

    def translate(self, text_line):
        translation = ''
        retry_count = 0
        translation_succeeded = False

        while not translation_succeeded and retry_count < self.retry_max:
            try:
                print('\nInput: {}'.format(text_line))
                translation, extra_data = translator.translate(text_line, target='NL') # self.language)
                print('translation: {}'.format(translation))
                print('Extra data: {}'.format(extra_data))
            except Exception as Exc:
                print(''.format(Exc))

            translation_succeeded = len(translation) != 0

            if not translation_succeeded:
                retry_count += 1
                time.sleep(5)

        return translation
