import re

class WtdReader:
    def __init__(self, docName):
        docName = str(docName)
        self.fileName = './DocumentosProcesados/wtd/' + docName + '.wtd'
        # Se lee el archivo .wtd
        self.file = open(self.fileName, "r")
        string = self.file.read()
        self.fileLines = string.split("\n")

    # Metodo que devuelve el archivo
    def getLinesWtd(self):
        return self.fileLines

    # Metodo que devuelve un diccionario de lo que tiene el .wtd
    # Llave: termino
    # Valor: Peso
    def getDicWtd(self):
        wtd = dict()
        for line in self.fileLines:
            lineWithoutSpace = re.sub(r'\s+', ' ', line)
            lineDiv = lineWithoutSpace.split(" ")
            if len(lineDiv) >= 2:
                wtd[lineDiv[0]] = float(lineDiv[1])
        return wtd


if __name__ == '__main__':
    tokReader = WtdReader('1_AP')
    wtd = tokReader.getDicWtd()
    for word in wtd:
        print(word + " " + str(wtd[word]))
