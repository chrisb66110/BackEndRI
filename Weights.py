from VocabularioReader import *
from TokReader import *
from FileGenerator import *

class Weights:
    def __init__(self):
        vocabularioReader = VocabularioReader('vocabulario')
        self.dicVoc = vocabularioReader.getDicVocabulario()

    # Metodo que devuelve un diccionario de pesos
    # Llave: termino
    # Valor: peso
    def getDicWeights(self, fileTokName):
        tokReader = TokReader(fileTokName)
        dicTok = tokReader.getDicTok()
        weights = dict()
        for term in dicTok.keys():
            #Posicion 1 del valor del dictTok es la frecuencia normalizada
            #Posicion 1 del valor del dicVoc es la frecuencia inversa
            weights[term] = dicTok[term][1] * self.dicVoc[term][1]
        return weights

    # Metodo para mandar a generar los archivos .wtd
    def generateWtd(self, filesName):
        generator = FileGenerator()
        for file in filesName:
            dicWeights = self.getDicWeights(file)
            generator.wtdGenerate(file, dicWeights)

# Main para prueba ver que genere los archivos .wtd
if __name__ == '__main__':
    filesName = '1_AP', '1_CT'
    weights = Weights()
    weights.generateWtd(filesName)