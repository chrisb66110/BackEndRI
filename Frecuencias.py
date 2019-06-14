import math

class TuplaVocabl:
    def __init__(self, numDocs, frecInversa):
        self.numDocs = numDocs
        self.frecInversa = frecInversa

    def getNumDocs(self):
        return self.numDocs

    def getFrecInversa(self):
        return self.frecInversa

class Frecuencias:

    def __init__(self):
        # Diccionario que guarda la palabra y la suma de las veces que sale en los documentos.
        self.numDocs = 750
        self.dictionary = dict()

    # Metodo que genera el diccionario de frecuencias
    # Recibe como parametro el diccionario de cada documento.
    # Devuelve un diccionario que los keys son las palabras del documento y los values
    def generateFrequency(self, dictionary):
        highestWordCount = 0
        freqDict = dict()
        # Buscamos la plabra con mayor frecuencia del documento.
        for word in dictionary:
            # Revisa que el diccionario general tenga la palabra y suma si aparece en un documento.
            if word in self.dictionary:
                value = self.dictionary[word]
                value += 1
                self.dictionary[word] = value
            else:
                self.dictionary[word] = 1
            # Busca la palabra con mayor peso en el documento
            if (dictionary[word] > highestWordCount):
                highestWordCount = dictionary[word]
                highestWord = word
        for word in dictionary:
            freq = dictionary[word]/highestWordCount
            freqDict[word] = freq
        return freqDict


    def generateVocabDic(self):
        vocabDict = dict()
        for word in self.dictionary:
            #Numero de veces que aparece el termino en el doc.
            numTermino = self.dictionary[word]
            # Generamos la frecuencia inversa.
            frecInversa = math.log(self.numDocs/self.dictionary[word])
            # Creamos el objeto que se guarda en el value.
            tuplaVocab = TuplaVocabl(numTermino, frecInversa)
            vocabDict[word] = tuplaVocab
        return vocabDict

    # Metodo que devuelve el diccionar de frecuecias normalizadas.
    def getDictionary(self):
        return self.dictionary
