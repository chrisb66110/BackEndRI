import operator
import json
from time import time

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
from WtdReader import *

app = Flask(__name__)

class Documento:
    def __init__(self, nombre, link, resumen):
        self.nombre = nombre
        self.link = link
        self.resumen = resumen

class Documentos:
    def __init__(self, listaDocumentos, cantidadDocumentos, tiempo):
        self.listaDocumentos = listaDocumentos
        self.cantidadDocumentos = cantidadDocumentos
        self.tiempo = tiempo

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
    def buscaDocumentosRealacionados(self, dictIndice, linesPonsting, wtdTodos):
        #indiceReader = IndiceReader('indice')
        #dictIndice = indiceReader.getDicIndice()
        # Key = termino
        # value: posinicial, cantEntradas
        docsInIndice = dict()
        # For para buscar las posiciones y la cantidad de documentos que tienen esa palabra en postings
        #for x in self.words:
        #    print(x)
        #start_time = time()
        for word in sorted(self.words):
            if word in dictIndice:
                docsInIndice[word] = dictIndice[word][0], dictIndice[word][1]
        #elapsed_time = time() - start_time
        #print("FOR CON SORT: %.10f seconds." % elapsed_time)
        # Dict de documentos
        # Key: doc
        # Value: dict de pesos:
        #                       Llave: termino
        #                       Valor: peso
        docs = dict()
        # For para buscar el nombre de los documentos en postings
        #start_time = time()
        for word in sorted(docsInIndice.keys()):
            cantEntradas = docsInIndice[word][1]
            primerLinea = docsInIndice[word][0]
            #print("CANTIDAD DE DOCUMENTOS: " + str(cantEntradas))
            for x in range(0, cantEntradas):
                linea = linesPonsting[primerLinea + x]
                lineaSinEspacios = re.sub(r'\s+', ' ', linea)
                lineDiv = lineaSinEspacios.split(" ")
                termino = lineDiv[0]
                documento = lineDiv[1]
                peso = lineDiv[2]
                # Genera el diccionario para obtener los pesos de la consulta.
                #weights = WtdReader(documento)
                #print("DOCUEMNTO: ", documento)
                #dicWeights = weights.getDicWtd()
                dicWeights = wtdTodos[documento]

                #start_time_interno = time()
                #vectPeso = self.agregar_terminos_que_no_tenga(dicWeights)
                #docs[documento] = vectPeso
                docs[documento] = dicWeights
                #elapsed_time_interno = time() - start_time_interno
                #print("2 for internos: %.10f seconds." % elapsed_time_interno)
        #elapsed_time = time() - start_time
        #print("2 for: %.10f seconds." % elapsed_time)
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
        #productoPunto = dict()
        #normaVect = dict()
        sumaProductoPunto = 0
        sumaNormaVect = 0
        for word in sorted(dictDoc.keys()):
            pesoDoc = dictDoc[word]
            pesoCon = dictConsulta[word]
            #if pesoCon != 0 and pesoCon != 0:
            #    print("pesoCon " + str(pesoCon) + ", pesoDoc " + str(pesoDoc))
            #productoPunto[word] = pesoDoc * pesoCon
            sumaProductoPunto = sumaProductoPunto + (pesoDoc * pesoCon)
            #normaVect[word] = pesoDoc * pesoDoc
            sumaNormaVect = sumaNormaVect + (pesoDoc * pesoDoc)
        #return productoPunto, normaVect
        raizSumaNormaVect = math.sqrt(sumaNormaVect)
        return sumaProductoPunto, raizSumaNormaVect

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
        sumaProductoPunto = dict()
        raizSumaNormaVect = dict()
        for doc in sorted(docs.keys()):
            dictPesosDoc = docs[doc]
            #start_time = time()
            sumaProductoPuntoYraizSumaNormaVect = self.productoPunto(dictPesosDoc, vectorConsulta)
            sumaProductoPunto[doc] = sumaProductoPuntoYraizSumaNormaVect[0]
            raizSumaNormaVect[doc] = sumaProductoPuntoYraizSumaNormaVect[1]
            #elapsed_time = time() - start_time

            #imprimir = '{:<75}'.format("productoPunto del doc " + doc)
            #print( imprimir + ": %.10f seconds." % elapsed_time)
            #docsProductoPunto[doc] = dictPesosNuevo
        #docsProductoPunto
        #KEY: DOCUMENTO
        #VALUE: sumaProductoPunto, raizSumaNormaVect
        return sumaProductoPunto, raizSumaNormaVect

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

    def sqrtconsultaNormaSumada(self, dictConsulta):
        suma = 0
        for word in sorted(dictConsulta.keys()):
            valVector = dictConsulta[word]
            suma = suma + valVector * valVector
        sqrtSuma = math.sqrt(suma)
        return sqrtSuma

def leerDocs(urlsDict):
    dictDoc = dict()
    for wordFile in sorted(urlsDict.keys()):
        nombreDoc = (wordFile.encode('ascii', 'ignore')).decode('utf-8')
        fileName = './DocumentosProcesados/DocsConExpresiones/' + nombreDoc + '.txt'
        file = open(fileName, "r")
        stringDoc = file.read()
        dictDoc[wordFile] = stringDoc
        # print("Doc: " + fileName)
        # print("Texto: " + str(stringDoc))
    print("Acabo de leer documentos")
    return dictDoc


def agregar_terminos_que_no_tenga (dicVoc, dicPesos):
    nuevodict = dict()
    for term in sorted(dicVoc.keys()):
        if term not in dicPesos:
            nuevodict[term] = 0
        else:
            nuevodict[term] = dicPesos[term]
    return nuevodict

def leerWtdTodos(dicVoc, urlsDict):
    dicWts = dict()
    for wordFile in sorted(urlsDict.keys()):
        nombreDoc = (wordFile.encode('ascii', 'ignore')).decode('utf-8')
        weights = WtdReader(nombreDoc)
        #print("DOCUEMNTO: ", documento)
        dicWtd = weights.getDicWtd()

        vectPeso = agregar_terminos_que_no_tenga(dicVoc, dicWtd)

        dicWts[nombreDoc] = vectPeso
        # print("Doc: " + fileName)
        # print("Texto: " + str(stringDoc))
    #print("Acabo de leer documentos")
    return dicWts
procConsultas = ProcConsultas()
indiceReader = IndiceReader('indice')
dictIndice = indiceReader.getDicIndice()
postingReader = PostingsReader('postings')
linesPonsting = postingReader.getLinesPostings()
urlsReader = URLsReader()
urlsDict = urlsReader.getDictUrls()
docsProcesados = leerDocs(urlsDict)
wtdTodos = leerWtdTodos(procConsultas.dicVoc, urlsDict)
@app.route('/<consulta>')
def hello_world(consulta):
    inicio = time()
    start_time = time()
    vectConsulta = procConsultas.generar_vector_consulta(consulta)
    elapsed_time = time() - start_time
    print("generar_vector_consulta: %.10f seconds." % elapsed_time)

    start_time = time()
    docsPesos = procConsultas.buscaDocumentosRealacionados(dictIndice, linesPonsting, wtdTodos)
    elapsed_time = time() - start_time
    print("buscaDocumentosRealacionados: %.10f seconds." % elapsed_time)

    #for doc in docsPesos.keys():
    #   print(doc + ': ' + str(docsPesos[doc]))

    start_time = time()
    sumaProductoPuntoYraizSumaNormaVect = procConsultas.productoPuntoTodosVectores(docsPesos,vectConsulta)
    #docsProductoPunto =
    elapsed_time = time() - start_time
    print("productoPuntoTodosVectores: %.10f seconds." % elapsed_time)
    #for doc in docsProductoPunto.keys():
    #   print(doc + ': ' + str(docsProductoPunto[doc]))

    start_time = time()
    #docsProductoPuntoSumado = procConsultas.sumaTodosVectores(docsProductoPunto)
    docsProductoPuntoSumado = sumaProductoPuntoYraizSumaNormaVect[0]
    elapsed_time = time() - start_time
    print("sumaTodosVectores: %.10f seconds." % elapsed_time)
    # for doc in docsProductoPuntoSumado.keys():
    #   print(doc + ': ' + str(docsProductoPuntoSumado[doc]))

    #start_time = time()
    #docsPesosNorma = procConsultas.normaTodosVectores(docsPesos)
    #elapsed_time = time() - start_time
    #print("normaTodosVectores: %.10f seconds." % elapsed_time)
    # for doc in docsPesosNorma.keys():
    #     print(doc + ': ' + str(docsPesosNorma[doc]))

    #start_time = time()
    #consultaPesosNorma = procConsultas.normaVector(vectConsulta)
    #elapsed_time = time() - start_time
    #print("normaVector: %.10f seconds." % elapsed_time)
    # for term in consultaPesosNorma.keys():
    #     print(term + ': ' + str(consultaPesosNorma[term]))

    #start_time = time()
    #docsNormaSumados = procConsultas.sumaTodosVectores(docsPesosNorma)
    #elapsed_time = time() - start_time
    #print("sumaTodosVectores: %.10f seconds." % elapsed_time)
    # for doc in docsNormaSumados.keys():
    #     print(doc + ': ' + str(docsNormaSumados[doc]))

    start_time = time()
    #consultaNormaSumada = procConsultas.sumaVector(consultaPesosNorma)
    elapsed_time = time() - start_time
    print("sumaVector: %.10f seconds." % elapsed_time)
    # print(consultaNormaSumada)

    start_time = time()
    #docsNormaSumadosRaiz = procConsultas.raizTodosVectores(docsNormaSumados)
    docsNormaSumadosRaiz = sumaProductoPuntoYraizSumaNormaVect[1]
    elapsed_time = time() - start_time
    print("raizTodosVectores: %.10f seconds." % elapsed_time)
    #for doc in docsNormaSumadosRaiz.keys():
    #    print(doc + ': ' + str(docsNormaSumadosRaiz[doc]))

    start_time = time()
    #consultaNormaSumadaRaiz = math.sqrt(consultaNormaSumada)
    consultaNormaSumadaRaiz = procConsultas.sqrtconsultaNormaSumada(vectConsulta)
    elapsed_time = time() - start_time
    print("sqrt: %.10f seconds." % elapsed_time)
    #print(consultaNormaSumadaRaiz)

    start_time = time()
    similaridad = procConsultas.similaridad(docsProductoPuntoSumado, docsNormaSumadosRaiz, consultaNormaSumadaRaiz)
    elapsed_time = time() - start_time
    print("similaridad: %.10f seconds." % elapsed_time)
    #for doc in sorted(similaridad.keys()):
    #    print(doc + ': ' + str(similaridad[doc]))

    start_time = time()
    #similaridad = { '5_AP': 0.5416401512051543, '1_AP': 0.4024963445340767 }
    ranking = sorted(similaridad.items(), key=operator.itemgetter(1))
    elapsed_time = time() - start_time
    print("sorted(similaridad.items(),key=operator.itemgetter(1)): %.10f seconds." % elapsed_time)
    #print(ranking[::-1])

    start_time = time()
    lista = list()
    largo = ranking.__len__()
    for x in range(0, largo):
        posActual = largo - x - 1
        nombreDocumento = str(ranking[posActual][0])
        linkDocumento = urlsDict[ranking[posActual][0]]
        #leerdoc = nombreDocumento + '.html'
        #htmlReader = HTMLReader(bytes(leerdoc, 'utf-8'))
        #htmlString = htmlReader.getHtml()
        #rules = Rules()
        string = docsProcesados[nombreDocumento] #rules.applyRules(htmlString)
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
    elapsed_time = time() - start_time
    print("ranking: %.10f seconds." % elapsed_time)

    fin = time() - inicio
    print("FIN: %.10f seconds." % fin)
    retornoDocumentos = Documentos(lista, lista.__len__(), fin)
    jsonStringTodo = json.dumps(retornoDocumentos, default=lambda o: o.__dict__, indent=4)
    #print(jsonStringTodo)

    #jsonString = json.dumps(lista, default=lambda o: o.__dict__, indent=4)
    #print(jsonString)
    return jsonStringTodo

if __name__ == '__main__':
    app.run()
