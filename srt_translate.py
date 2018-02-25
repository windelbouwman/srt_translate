#!/usr/bin/python

""" Translate subtitles.

"""
# TODO:
# Fix funny characters in output file, reason unknown..

import argparse
import srt
import chardet
from googletrans import Translator
from os import path
from progress.bar import IncrementalBar


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument( '-file', help='SRT subtitle file to translate')
    parser.add_argument('-language', help='The language to which to translate e.g. "nl"')
    args = parser.parse_args()

    if args.file is None or args.language is None:
        parser.print_help()
        print('')
        raise SyntaxError('One or more argument is missing')

    input_file_name = args.file
    language = args.language

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

    print('\nSuccesfully translated the SRT file.')
    print('Output saved as: {}'.format(output_file_name))

def get_file_encoding(filename):
    raw = open(filename, 'rb').read()
    result = chardet.detect(raw)
    return result['encoding']


class SrtTranslator:
    """ Object which can translate srt subtitles """
    def __init__(self, language):
        self.language = language

    def translate(self, srt_data):
        translator = Translator()

        subs = list(srt.parse(srt_data))
        bar = IncrementalBar('Translating', max=len(subs))

        try:
            for sub in subs:
                # print('sub: {}'.format(sub.content))
                sub.content = translator.translate(sub.content, dest=self.language).text
                # print('translated-sub: {}'.format(sub.content))
                bar.next()
        except Exception as Exc:
            print('Operation failed due to exception: {}'.format(Exc))

        bar.finish()

        return srt.compose(subs)


if __name__ == '__main__':
    main()
