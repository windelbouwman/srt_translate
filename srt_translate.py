#!/usr/bin/python

""" Translate subtitles.

"""


import argparse
import srt


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'original',
        type=argparse.FileType('r', encoding='utf8'),
        help='Original srt subtitle file to translate')
    parser.add_argument('language', help='The language to which to translate')
    parser.add_argument('translated', type=argparse.FileType('w'))
    args = parser.parse_args()
    language = args.language
    srt_translator = SrtTranslator(language)
    args.translated.write(srt_translator.translate(args.original.read()))


class SrtTranslator:
    """ Object which can translate srt subtitles """
    def __init__(self, language):
        self.language = language

    def translate(self, srt_data):
        """ Translate the given subtitle """
        # Strip BOM (byte order marker):
        if srt_data[0] == chr(0xfeff):
            srt_data = srt_data[1:]

        # print(srt_data[:20].encode('ascii'), type(srt_data))
        return srt.compose(
            map(self._translate_subtitle, srt.parse(srt_data)))

    def _translate_subtitle(self, subtitle: srt.Subtitle) -> srt.Subtitle:
        """ Translate a single subtitle object """
        content = self._translate_text(subtitle.content)
        return srt.Subtitle(
            subtitle.index, subtitle.start, subtitle.end, content)

    def _translate_text(self, text: str) -> str:
        # TODO
        return text


if __name__ == '__main__':
    main()
