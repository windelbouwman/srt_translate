from translator_class import TranslateClass
from googletrans import Translator


class GoogleTranslator(TranslateClass):
    """ Object which can translate srt subtitles """
    translator = Translator()
    retry_max = 3
    zero_width_space_char = u'\u200B'
    trans_table = dict.fromkeys(map(ord, zero_width_space_char), None)

    def translate(self, text_line):
        retry_count = 0
        translation_succeeded = False
        exception_message = ''

        while not translation_succeeded and retry_count < self.retry_max:
            try:
                translated_line = self.translator.translate(text_line, dest=self.language).text
                translation_succeeded = True
            except Exception as Exc:
                exception_message = str('\nError: {}'.format(Exc))
                print('\nTranslation failed, trying again.. (try count: {} max. tries: {})'.format(retry_count, self.retry_max))
                retry_count += 1
                self.translator = Translator()      # I don't know what happens here but this helps :-)

        if not translation_succeeded:
            print(exception_message)
            print('Exception occurred while trying to get a translation for:\n\"{}\"\n'.format(text_line))
            raise RuntimeError

        # Remove zero-width char's if any (Google translate bug that adds zero-width char's for no-reason)
        return translated_line.translate(self.trans_table)


