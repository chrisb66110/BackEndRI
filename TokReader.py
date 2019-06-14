import re

class TokReader:
    def __init__(self, docName):
        docName = str(docName)
        self.fileName = './DocumentosProcesados/tok/' + docName + '.tok'
        # Se lee el archivo .tok
        self.file = open(self.fileName, "r")
        string = self.file.read()
        self.fileLines = string.split("\n")

    # Metodo que devuelve el archivo
    def getLinesTok(self):
        return self.fileLines

    # Metodo que devuelve un diccionario de lo que tiene el .tok
    # Llave: termino
    # Valor: Frecuencia, FrecuenciaNormalizada
    def getDicTok(self):
        tok = dict()
        for line in self.fileLines:
            lineWithoutSpace = re.sub(r'\s+', ' ', line)
            lineDiv = lineWithoutSpace.split(" ")
            if len(lineDiv) >= 3:
                tok[lineDiv[0]] = float(lineDiv[1]), float(lineDiv[2])
        return tok


if __name__ == '__main__':
    tokReader = TokReader('hacking6')
    tok = tokReader.getDicTok()
    for word in tok:
        print(word + str(tok[word]))
