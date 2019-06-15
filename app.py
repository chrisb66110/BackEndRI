import operator
import json

from flask import Flask

from Rules import *
from DocWordCounter import *
from URLsReader import *
from Frecuencias import *
from Weights import *
from IndiceReader import *
from PostingsReader import *
from VocabularioReader import *
from  HTMLReader import *

app = Flask(__name__)

class Documento:
    def __init__(self, nombre, link, resumen):
        self.nombre = nombre
        self.link = link
        self.resumen = resumen

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
            #if pesoCon != 0 and pesoCon != 0:
            #    print("pesoCon " + str(pesoCon) + ", pesoDoc " + str(pesoDoc))
            productoPunto[word] = pesoDoc * pesoCon
        return productoPunto

    # dictDoc Diccionario del vector
    #   Llave: termino
    #   Valor: peso
    #
    # Retorna valor de la suma
    def sumaVector(self, dictVec):
        suma = 0.0
        for word in sorted(dictVec.keys()):
            suma = suma + dictVec[word]
        return suma

    # dictDoc Diccionario del vector
    #   Llave: termino
    #   Valor: peso
    #
    # Retorna dict del vector con la norma aplicada
    def normaVector(self, dictVec):
        norma = dict()
        for word in sorted(dictVec.keys()):
            valVector = dictVec[word]
            norma[word] = valVector * valVector
        return norma

    # Metodo para hacer el producto punto de todos vectores de los documentos con el vector de la consulta
    # docs Diccionario de documentos
    #       Key: doc
    #       Value: dict vector de pesos:
    #                               Llave: termino
    #                               Valor: peso
    #
    # vectorConsulta vector de consulta
    #       Llave: termino
    #       Valor: peso
    #
    # Retorna dict del vector con la norma aplicada
    def productoPuntoTodosVectores(self, docs, vectorConsulta):
        docsProductoPunto = dict()
        for doc in sorted(docs.keys()):
            dictPesosDoc = docs[doc]
            dictPesosNuevo = self.productoPunto(dictPesosDoc, vectorConsulta)
            docsProductoPunto[doc] = dictPesosNuevo
        return docsProductoPunto

    # Metodo para hacer la suma de todas las entradas de todos los vectores
    # docs Diccionario de documentos
    #       Key: doc
    #       Value: dict vector de pesos:
    #                               Llave: termino
    #                               Valor: peso
    #
    # retorna dict con todos los documentos con su vector sumado
    def sumaTodosVectores(self, docs):
        docsSumados = dict()
        for doc in sorted(docs.keys()):
            dictPesosDoc = docs[doc]
            suma = self.sumaVector(dictPesosDoc)
            docsSumados[doc] = suma
        return docsSumados

    # Metodo para le aplica la norma a todos los vectores
    # docs Diccionario de documentos
    #       Key: doc
    #       Value: dict vector de pesos:
    #                               Llave: termino
    #                               Valor: peso
    #
    # retorna dict con todos los documentos con su vector sumado
    def normaTodosVectores(self, docs):
        docsNorma = dict()
        for doc in sorted(docs.keys()):
            dictPesosDoc = docs[doc]
            normaVector = self.normaVector(dictPesosDoc)
            docsNorma[doc] = normaVector
        return docsNorma

    # Metodo para aplica la raiz a la suma de todos los vectores
    # docs Diccionario de documentos
    #       Key: doc
    #       Value: suma del vector
    # retorna dict con todos los documentos con su vector sumado con raiz
    def raizTodosVectores(self, docs):
        docsRaiz = dict()
        for doc in sorted(docs.keys()):
            suma = docs[doc]
            docsRaiz[doc] = math.sqrt(suma)
        return docsRaiz

    # Metodo para aplicar la similaridad
    # docsProductoPunto Suma del vector del producto punto de documentos
    #   Key: docs
    #   Value: Suma del vector del producto punto de documentos
    #
    # docsNormaSumadosRaiz Diccionario de consulta
    #   Key: docs
    #   Value: suma de vector con raiz
    #
    # consultaNormaSumadaRaiz Diccionario de consulta
    #       Key: termino
    #       Value: suma de vector con raiz
    #
    # retorna dict con todos los documentos con su vector sumado con raiz
    def similaridad(self, docsProductoPunto, docsNormaSumadosRaiz, consultaNormaSumadaRaiz):
        docsSimilaridad = dict()
        for doc in sorted(docsProductoPunto.keys()):
            sumaVecDocProductoPunto = docsProductoPunto[doc]
            sumaVecDocNorma = docsNormaSumadosRaiz[doc]

            similaridad = sumaVecDocProductoPunto / ( sumaVecDocNorma * consultaNormaSumadaRaiz )
            docsSimilaridad[doc] = similaridad
        return docsSimilaridad

procConsultas = ProcConsultas()
indiceReader = IndiceReader('indice')
dictIndice = indiceReader.getDicIndice()
postingReader = PostingsReader('postings')
linesPonsting = postingReader.getLinesPostings()
urlsReader = URLsReader()
urlsDict = urlsReader.getDictUrls()
@app.route('/<consulta>')
def hello_world(consulta):
    vectConsulta = procConsultas.generar_vector_consulta(consulta)
    docsPesos = procConsultas.buscaDocumentosRealacionados(dictIndice, linesPonsting)

    #for doc in docsPesos.keys():
    #   print(doc + ': ' + str(docsPesos[doc]))

    docsProductoPunto = procConsultas.productoPuntoTodosVectores(docsPesos,vectConsulta)
    #for doc in docsProductoPunto.keys():
    #   print(doc + ': ' + str(docsProductoPunto[doc]))

    docsProductoPuntoSumado = procConsultas.sumaTodosVectores(docsProductoPunto)
    # for doc in docsProductoPuntoSumado.keys():
    #   print(doc + ': ' + str(docsProductoPuntoSumado[doc]))

    docsPesosNorma = procConsultas.normaTodosVectores(docsPesos)
    # for doc in docsPesosNorma.keys():
    #     print(doc + ': ' + str(docsPesosNorma[doc]))

    consultaPesosNorma = procConsultas.normaVector(vectConsulta)
    # for term in consultaPesosNorma.keys():
    #     print(term + ': ' + str(consultaPesosNorma[term]))

    docsNormaSumados = procConsultas.sumaTodosVectores(docsPesosNorma)
    # for doc in docsNormaSumados.keys():
    #     print(doc + ': ' + str(docsNormaSumados[doc]))

    consultaNormaSumada = procConsultas.sumaVector(consultaPesosNorma)
    # print(consultaNormaSumada)

    docsNormaSumadosRaiz = procConsultas.raizTodosVectores(docsNormaSumados)
    #for doc in docsNormaSumadosRaiz.keys():
    #    print(doc + ': ' + str(docsNormaSumadosRaiz[doc]))

    consultaNormaSumadaRaiz = math.sqrt(consultaNormaSumada)
    #print(consultaNormaSumadaRaiz)

    similaridad = procConsultas.similaridad(docsProductoPuntoSumado, docsNormaSumadosRaiz, consultaNormaSumadaRaiz)
    #for doc in sorted(similaridad.keys()):
    #    print(doc + ': ' + str(similaridad[doc]))

    #similaridad = { '5_AP': 0.5416401512051543, '1_AP': 0.4024963445340767 }
    ranking = sorted(similaridad.items(), key=operator.itemgetter(1))
    #print(ranking[::-1])
    lista = list()
    largo = ranking.__len__()
    for x in range(0, largo):
        posActual = largo - x - 1
        nombreDocumento = str(ranking[posActual][0])
        linkDocumento = urlsDict[ranking[posActual][0]]
        leerdoc = nombreDocumento + '.html'
        htmlReader = HTMLReader(bytes(leerdoc, 'utf-8'))
        htmlString = htmlReader.getHtml()
        rules = Rules()
        string = rules.applyRules(htmlString)
        #print(string)
        #print(stringB)
        #string = re.sub('', '', str(stringB, 'utf-8'))
        resu = '...'
        for word in procConsultas.words:
            index = string.lower().find(' '+ word +' ')
            #print(str(index))
            if index != None:
                resu = resu + string[index:index+60]
                break
        resumen = resu + '...'
        #print(str(posActual) + ': ' + str(ranking[posActual]))
        #print('Nombre del documento: ' + nombreDocumento)
        #print('Link del documento: ' + linkDocumento)
        #print('Resumen del result: ' + resumen)
        lista.append(Documento(nombreDocumento, linkDocumento, resumen))
    #for x in lista:
    #    print(x.nombre)
    #    print(x.link)
    #    print(x.resumen)
    #list_example = [Documento('Hola1','http1','resumen1'), Documento('Hola2','http2','resumen2')]
    #print(json.dumps(list_example))
    return json.dumps(lista, default=lambda o: o.__dict__, indent=4)

if __name__ == '__main__':
    app.run()
