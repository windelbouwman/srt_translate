#!/usr/bin/python

""" Translate subtitles.

"""

import argparse
import srt
import chardet
import time
from os import path
from google_translator import GoogleTranslator
from deepl_translator import DeeplTranslator
from progress.bar import IncrementalBar


def main():
    parser = argparse.ArgumentParser()
    help_text_language = 'The language to which to translate e.g. "nl"'
    help_text_language += '\nCheck for language codes:'
    help_text_language += '\nhttps://sites.google.com/site/tomihasa/google-language-codes'
    parser.add_argument('-file', help='SRT subtitle file to translate')
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

        srt_translator = GoogleTranslator(language)
        #srt_translator = DeeplTranslator(language)

        subs = list(srt.parse(input_file_data))
        progress_bar = IncrementalBar('Translating', max=len(subs))

        for sub in subs:
            merge_is_needed = sub_merge_needed(sub.content)
            if merge_is_needed:
                text_to_be_translated, newline_count = remove_newline_char_from_line(sub.content)
                line_to_add_newlines = srt_translator.translate(text_to_be_translated)
                sub.content = add_newline_char_to_line(line_to_add_newlines, newline_count)
            else:
                sub.content = srt_translator.translate(sub.content)
            # print('translated-sub: {}'.format(sub.content))
            progress_bar.next()

        progress_bar.finish()
        srt_translation = srt.compose(subs)

        output_file = open(output_file_name, "w", encoding='utf-8')
        output_file.write(srt_translation)

        t1 = time.clock()

        print('\nSuccessfully translated the SRT file.')
        print('This translation took {:.2F} seconds to complete.'.format(t1-t0))
        print('Output saved as: {}'.format(output_file_name))
    except Exception as Exc:
        print('\nOperation failed due to an exception.')


def get_file_encoding(filename):
    raw = open(filename, 'rb').read()
    result = chardet.detect(raw)
    return result['encoding']


def remove_newline_char_from_line(line):
    count = line.count('\n')
    return line.replace('\n', ' '), count


def add_newline_char_to_line(line, count):
    splitted_line = line.split()
    amount_of_words = len(splitted_line)
    word_offset = int(amount_of_words / (count+1)) + 1
    combined_sentence = ''
    for count in range(amount_of_words):
        combined_sentence += splitted_line[count] + ' '
        if (count+1) % word_offset == 0:
            combined_sentence += '\n'
    return combined_sentence


# Decides if merging lines (can result in a better translation)
# is desired or not
def sub_merge_needed(line):
    lines = line.split('\n')
    if len(lines) > 1:
        # If a dialog (starts with '-') or capital letter, don't merge line
        if lines[1][0] == '-' or lines[1][0].isupper():
            return False
    return True


if __name__ == '__main__':
    main()
