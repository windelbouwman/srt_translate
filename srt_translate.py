#!/usr/bin/python

""" Translate subtitles.

"""
# TODO:
# 1 - determine if there is a BOM and if yes, skip the length of it
# 2 - detect encoding of the input file, using chardet?


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

    print('input file: {}'.format(input_file_name))
    print('output file: {}'.format(output_file_name))
    print('Please wait, this may take a while..')

    input_file = open(args.file, "r")
    input_file_data = input_file.read()

    srt_translator = SrtTranslator(language)
    srt_translation = srt_translator.translate(input_file_data)

    output_file = open(output_file_name, "w", encoding='utf8')
    output_file.write(srt_translation)

    print('Succesfully translated the SRT file, output saved as: {}'.format(output_file_name))


class SrtTranslator:
    """ Object which can translate srt subtitles """
    def __init__(self, language):
        self.language = language

    def translate(self, srt_data):
        translator = Translator()
        """ Translate the given subtitle """
        # Strip BOM (byte order marker):
        if srt_data[0] == chr(0xfeff):
            srt_data = srt_data[1:]

        srt_data = srt_data[3:]

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
