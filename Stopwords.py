class Stopwords:
    def __init__(self):
        self.articulos = './Stopwords/articulos.txt'
        self.conjunciones = './Stopwords/conjunciones.txt'
        self.preposiciones = './Stopwords/preposiciones.txt'

    def getStopWords(self):
        # Se abre el archivo para ser leido.
        articulosFile = open(self.articulos, "r")
        readArticulos = articulosFile.read()
        conjuncionesFile = open(self.conjunciones, "r")
        readConjunciones = conjuncionesFile.read()
        preposicionesFile = open(self.preposiciones, "r")
        readPreposiciones = preposicionesFile.read()

        # Se separaron las palabras que llevan espacios y se hace un vector.
        separateArticulos = readArticulos.split(' ')
        separateConjunciones = readConjunciones.split(' ')
        separatePreposiciones = readPreposiciones.split(' ')

        # Concatenamos el vector de stopwords
        stopwords = separateArticulos + separateConjunciones + separatePreposiciones

        # Creamos un diccionario de los stopwords.
        dictionary = [word for word in stopwords]
        return dictionary

