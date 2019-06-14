import re

class VocabularioReader:
    def __init__(self, docName):
        docName = str(docName)
        self.fileName = './DocumentosProcesados/vocabulario/' + docName + '.txt'
        # Se lee el archivo vocabulario
        self.file = open(self.fileName, "r")
        string = self.file.read()
        self.fileLines = string.split("\n")


    # Metodo que devuelve el archivo
    def getLinesTok(self):
        return self.fileLines

    # Metodo que devuelve un diccionario de lo que tiene vocabulario
    # Llave: termino
    # Valor: numeroDocumentosDondeEstaElArchivo, FrecuenciaInversa
    def getDicVocabulario(self):
        voc = dict()
        for line in self.fileLines:
            lineWithoutSpace = re.sub(r'\s+', ' ', line)
            lineDiv = lineWithoutSpace.split(" ")
            if len(lineDiv) >= 3:
                voc[lineDiv[0]] = float(lineDiv[1]), float(lineDiv[2])
        return voc


if __name__ == '__main__':
    vocabularioReader = VocabularioReader('vocabulario')
    voc = vocabularioReader.getDicVocabulario()
    for word in voc:
        print(word + str(voc[word]))