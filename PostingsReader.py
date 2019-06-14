import re

class PostingsReader:
    def __init__(self, docName):
        docName = str(docName)
        self.fileName = './DocumentosProcesados/postings/' + docName + '.txt'
        # Se lee el archivo .wtd
        self.file = open(self.fileName, "r")
        string = self.file.read()
        self.fileLines = string.split("\n")

    # Metodo que devuelve el archivo
    def getLinesPostings(self):
        return self.fileLines

    # Metodo que devuelve un diccionario de lo que tiene el portings.txt
    # Llave: termino, aliasDocumento
    # Valor: numeroLinea, peso
    def getDicPostings(self):
        postings = dict()
        numberLine = 0
        for line in self.fileLines:
            lineWithoutSpace = re.sub(r'\s+', ' ', line)
            lineDiv = lineWithoutSpace.split(" ")
            if len(lineDiv) >= 3:
                llave = lineDiv[0], lineDiv[1]
                postings[llave] = numberLine, float(lineDiv[2])
                numberLine = numberLine + 1
        return postings

if __name__ == '__main__':
    tokReader = PostingsReader('postings')
    wtd = tokReader.getDicPostings()
    for word in wtd:
        print(str(word) + " " + str(wtd[word]))
