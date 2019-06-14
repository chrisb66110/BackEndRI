from flask import Flask

from Rules import *
from DocWordCounter import *
from URLsReader import *
from Frecuencias import *
from Weights import *
from IndiceReader import *
from PostingsReader import *
from VocabularioReader import *

app = Flask(__name__)

class ProcConsultas:

    def __init__(self):
        vocabularioReader = VocabularioReader('vocabulario')
        self.dicVoc = vocabularioReader.getDicVocabulario()

    def agregar_terminos_que_no_tenga(self, dicPesos):
        nuevodict = dict()
        for term in sorted(self.dicVoc.keys()):
            if term not in dicPesos:
                nuevodict[term] = 0
            else:
                nuevodict[term] = dicPesos[term]
        return nuevodict


    def generar_vector_consulta(self, consulta):
        # Nombre para archivos que se generan con la consulta
        fileName = '_consulta'

        # Se le aplican las reglas a la consulta
        rules = Rules()
        words = rules.applyRules(consulta)
        # Se cuentan las palabran dentro de la consulta
        requestWordCount = DocWordCounter(fileName, words)
        # Se quitan los stopwords de la consulta
        requestWordCount.generateStopWordsDict()
        # Separa las palabras y las agrega en un diccionario de la consulta.
        requestWordCount.separateWords()
        self.words = requestWordCount.wordVector
        #for x in self.words:
        #    print(x)
        wordDict = requestWordCount.generateDict()
        # Se genera un diccionario de la frecuencia.
        freq = Frecuencias()
        freqDict = freq.generateFrequency(wordDict)
        #print("Frecuencia= " + str(freqDict['protectora']))

        # Genera el .tok de la consulta
        generador = FileGenerator()
        generador.tokGenerate(fileName, wordDict, freqDict)

        # Genera el diccionario para obtener los pesos de la consulta.
        weights = Weights()
        dicWeights = weights.getDicWeightsConsulta(fileName)

        vect = self.agregar_terminos_que_no_tenga(dicWeights)
        #for term in vect.keys():
        #    print(term + ': ' + str(vect[term]))
        return vect

    # dictIndice diccionario del indice
    #      Llave: termino
    #      Valor: posinicial, cantEntradas
    #
    # postingReader diccionario de postings
    #
    # Retorna diccionario
    # Key: doc
    # Value: dict de pesos:
    #                       Llave: termino
    #                       Valor: peso
    def buscaDocumentosRealacionados(self, dictIndice, linesPonsting):
        #indiceReader = IndiceReader('indice')
        #dictIndice = indiceReader.getDicIndice()
        # Key = termino
        # value: posinicial, cantEntradas
        docsInIndice = dict()
        # For para buscar las posiciones y la cantidad de documentos que tienen esa palabra en postings
        #for x in self.words:
        #    print(x)
        for word in sorted(self.words):
            if word in dictIndice:
                docsInIndice[word] = dictIndice[word][0], dictIndice[word][1]
        # Dict de documentos
        # Key: doc
        # Value: dict de pesos:
        #                       Llave: termino
        #                       Valor: peso
        docs = dict()
        # For para buscar el nombre de los documentos en postings
        for word in sorted(docsInIndice.keys()):
            cantEntradas = docsInIndice[word][1]
            primerLinea = docsInIndice[word][0]
            for x in range(0, cantEntradas):
                linea = linesPonsting[primerLinea + x]
                lineaSinEspacios = re.sub(r'\s+', ' ', linea)
                lineDiv = lineaSinEspacios.split(" ")
                termino = lineDiv[0]
                documento = lineDiv[1]
                peso = lineDiv[2]
                # Genera el diccionario para obtener los pesos de la consulta.
                weights = Weights()
                dicWeights = weights.getDicWeightsConsulta(documento)

                vectPeso = self.agregar_terminos_que_no_tenga(dicWeights)
                docs[documento] = vectPeso
        return docs

    # dictDoc Diccionario del documento
    #   Llave: termino
    #   Valor: peso
    #
    # dictConsulta Diccionario de la consulta
    #   Llave: termino
    #   Valor: peso
    #
    # Retorna diccionario del producto punto
    #   Llave: termino
    #   Valor: peso
    def productoPunto(self, dictDoc, dictConsulta):
        productoPunto = dict()
        for word in sorted(dictDoc.keys()):
            pesoDoc = dictDoc[word]
            pesoCon = dictConsulta[word]
            productoPunto[word] = pesoDoc * pesoCon
        return productoPunto


procConsultas = ProcConsultas()
indiceReader = IndiceReader('indice')
dictIndice = indiceReader.getDicIndice()
postingReader = PostingsReader('postings')
linesPonsting = postingReader.getLinesPostings()
@app.route('/<consulta>')
def hello_world(consulta):
    procConsultas.generar_vector_consulta(consulta)
    docs = procConsultas.buscaDocumentosRealacionados(dictIndice, linesPonsting)

    for term in docs.keys():
       print(term + ': ' + str(docs[term].__len__()))

    return consulta

if __name__ == '__main__':
    app.run()
