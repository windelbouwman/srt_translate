from abc import abstractmethod


class TranslateClass:
    def __init__(self, language):
        self.language = language

    @abstractmethod
    def translate(self, text_line):
        raise NotImplemented
