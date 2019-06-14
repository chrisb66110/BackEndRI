from Stopwords import *

class DocWordCounter:

    def __init__(self, docName, docString):
        # Creamos un diccionario para guardar las palabras, key = Palabra  Value = # de veces que esta la palabra
        self.docName = docName
        self.docString = docString
        self.wordVector = None
        self.stopwordsDict = None
        self.dictionary = dict()

    # Genera un vector con la palabras de cada documento.
    def separateWords(self):
        self.wordVector = self.docString.split(' ')

    def generateStopWordsDict(self):
        stopwords = Stopwords()
        self.stopwordsDict = stopwords.getStopWords()

    def generateDict(self):
        for word in self.wordVector:
            if word not in self.stopwordsDict:
                if word in self.dictionary:
                    # Caso en que ya exista el valor se le agrega 1 al value,
                    # que representa sumar la cantidad  de palabras que hay.
                    value = self.dictionary.get(word)
                    value = value + 1
                    self.dictionary[word] = value
                else:
                    # Caso en que no exista la palabra se agrega al diciconario.
                    self.dictionary[word] = 1
        return self.dictionary

