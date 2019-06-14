from PostingsReader import *
from FileGenerator import *

class Indice:

    # Metodo que devuelve un diccionario de Postings
    # Llave: termino
    # Valor: posinicial, cantEntradas
    def getDicIndice(self):
        dicIndice = dict()
        postingsReader = PostingsReader('postings')
        dicPosting = postingsReader.getDicPostings()
        palabrasNuevas = 0
        for wordFile in dicPosting:
            if wordFile[0] in dicIndice:
                if dicIndice[wordFile[0]][0] > dicPosting[wordFile][0]:
                    dicIndice[wordFile[0]] = dicPosting[wordFile][0], dicIndice[wordFile[0]][1] + 1
                else:
                    dicIndice[wordFile[0]] = dicIndice[wordFile[0]][0], dicIndice[wordFile[0]][1] + 1
            else:
                palabrasNuevas = palabrasNuevas + 1
                dicIndice[wordFile[0]] = dicPosting[wordFile][0], 1
        return dicIndice

    def generateIndice(self):
        dicIndice = self.getDicIndice()
        generator = FileGenerator()
        generator.indiceGenerate('indice', dicIndice)

# Main para prueba ver que genere los archivos .wtd
if __name__ == '__main__':
    indice = Indice()
    indice.generateIndice()