#!/usr/bin/python

""" Translate subtitles.

"""

import argparse
import srt
import chardet
import time
from googletrans import Translator
from os import path
from progress.bar import IncrementalBar


def main():
    parser = argparse.ArgumentParser()
    help_text_language = 'The language to which to translate e.g. "nl"'
    help_text_language += '\nCheck for language codes:'
    help_text_language += '\nhttps://sites.google.com/site/tomihasa/google-language-codes'
    parser.add_argument( '-file', help='SRT subtitle file to translate')
    parser.add_argument('-language', help=help_text_language)
    args = parser.parse_args()

    if args.file is None or args.language is None:
        parser.print_help()
        print('')
        raise SyntaxError('One or more argument is missing')

    t0 = time.clock()

    input_file_name = args.file
    language = args.language

    try:
        output_file_name, file_extension = path.splitext(input_file_name)
        output_file_name = output_file_name + '.' + args.language + file_extension
        file_encoding = get_file_encoding(args.file)

        print('\n')
        print('Input file:          {}'.format(input_file_name))
        print('Input file encoding: {}'.format(file_encoding))
        print('Output file:         {}\n'.format(output_file_name))

        input_file = open(args.file, "r", encoding=file_encoding)
        input_file_data = input_file.read()

        srt_translator = SrtTranslator(language)
        srt_translation = srt_translator.translate(input_file_data)

        output_file = open(output_file_name, "w", encoding='utf-8')
        output_file.write(srt_translation)

        t1 = time.clock()

        print('\nSuccesfully translated the SRT file.')
        print('This translation took {:.2F} seconds to complete.'.format(t1-t0))
        print('Output saved as: {}'.format(output_file_name))
    except Exception as Exc:
        print('\nOperation failed due to an exception.')

def get_file_encoding(filename):
    raw = open(filename, 'rb').read()
    result = chardet.detect(raw)
    return result['encoding']


class SrtTranslator:
    """ Object which can translate srt subtitles """
    def __init__(self, language):
        self.language = language
        self.zw_space_char = u'\u200B'
        self.trans_table = dict.fromkeys(map(ord, self.zw_space_char), None)

    def translate(self, srt_data):
        translator = Translator()
        retry_max = 3
        retry_count = 0
        translation_succeeded = False

        subs = list(srt.parse(srt_data))
        progress_bar = IncrementalBar('Translating', max=len(subs))

        for sub in subs:
            retry_count = 0
            translation_succeeded = False

            # print('sub: {}'.format(sub.content))
            text_to_be_translated, newline_count = self.remove_newline_char_from_line(sub.content)

            while not translation_succeeded and retry_count < retry_max:
                try:
                    translated_line = translator.translate(text_to_be_translated, dest=self.language).text 
                    translation_succeeded = True
                except Exception as Exc:
                    exception_message = str('\nError: {}'.format(Exc))
                    print('\nTranslation failed, trying again.. (try count: {} max. tries: {})'.format(retry_count, retry_max))
                    retry_count += 1
                    time.sleep(1)

            if not translation_succeeded:
                print(exception_message)
                print('Exception occurred while trying to get a translation for:\n\"{}\"\n'.format(text_to_be_translated))
                raise RuntimeError

            # Remove zero-width char's if any (Google translate bug that adds zero-width char's for no-reason)
            line_to_add_newlines = translated_line.translate(self.trans_table)

            sub.content = self.add_newline_char_to_line(line_to_add_newlines, newline_count)
            # print('translated-sub: {}'.format(sub.content))

            progress_bar.next()

        progress_bar.finish()
        return srt.compose(subs)

    def remove_newline_char_from_line(self, line):
        count = line.count('\n')
        return line.replace('\n', ' '), count

    def add_newline_char_to_line(self, line, count):
        splitted_line = line.split()
        amount_of_words = len(splitted_line)
        word_offset = int(amount_of_words / (count+1)) + 1
        combined_sentence = ''
        for count in range(amount_of_words):
            combined_sentence += splitted_line[count] + ' '
            if (count+1) % word_offset == 0:
                combined_sentence += '\n'
        return combined_sentence


if __name__ == '__main__':
    main()
