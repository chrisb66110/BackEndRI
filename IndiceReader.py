import re

class IndiceReader:
    def __init__(self, docName):
        docName = str(docName)
        self.fileName = './DocumentosProcesados/indice/' + docName + '.txt'
        # Se lee el archivo indice
        self.file = open(self.fileName, "r")
        string = self.file.read()
        self.fileLines = string.split("\n")

    # Metodo que devuelve el archivo
    def getLinesIndice(self):
        return self.fileLines

    # Metodo que devuelve un diccionario de Postings
    # Llave: termino
    # Valor: posinicial, cantEntradas
    def getDicIndice(self):
        indice = dict()
        for line in self.fileLines:
            lineWithoutSpace = re.sub(r'\s+', ' ', line)
            lineDiv = lineWithoutSpace.split(" ")
            if len(lineDiv) >= 3:
                term = lineDiv[0]
                indice[term] = int(lineDiv[1]), int(lineDiv[2])
        return indice

if __name__ == '__main__':
    tokReader = IndiceReader('indice')
    wtd = tokReader.getDicIndice()
    for word in wtd:
        print(str(word) + " " + str(wtd[word]))
