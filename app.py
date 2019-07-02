import operator
import json
from time import time
from flask_cors import CORS, cross_origin
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
from collections import Counter

app = Flask(__name__)
cors = CORS(app)

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
        wordDict = requestWordCount.generateDict()
        self.words = requestWordCount.wordVector
        # Se genera un diccionario de la frecuencia.
        freq = Frecuencias()
        freqDict = freq.generateFrequency(wordDict)
        # Genera el .tok de la consulta
        generador = FileGenerator()
        generador.tokGenerate(fileName, wordDict, freqDict)
        # Genera el diccionario para obtener los pesos de la consulta.
        weights = Weights()
        dicWeights = weights.getDicWeightsConsulta(fileName)
        vect = self.agregar_terminos_que_no_tenga(dicWeights)
        return vect

    def buscaDocumentosRealacionados(self, dictIndice, linesPonsting, wtdTodos):
        docsInIndice = dict()
        # For para buscar las posiciones y la cantidad de documentos que tienen esa palabra en postings
        for word in sorted(self.words):
            if word in dictIndice:
                docsInIndice[word] = dictIndice[word][0], dictIndice[word][1]
        docs = dict()
        # For para buscar el nombre de los documentos en postings
        for word in sorted(docsInIndice.keys()):
            cantEntradas = docsInIndice[word][1]
            primerLinea = docsInIndice[word][0]
            for x in range(0, cantEntradas):
                linea = linesPonsting[primerLinea + x]
                lineaSinEspacios = re.sub(r'\s+', ' ', linea)
                lineDiv = lineaSinEspacios.split(" ")
                documento = lineDiv[1]
                # Genera el diccionario para obtener los pesos de la consulta.
                dicWeights = wtdTodos[documento]
                docs[documento] = dicWeights
        return docs

    def productoPunto(self, dictDoc, dictConsulta):
        sumaProductoPunto = 0
        sumaNormaVect = 0
        for word in sorted(dictDoc.keys()):
            pesoDoc = dictDoc[word]
            pesoCon = dictConsulta[word]
            sumaProductoPunto = sumaProductoPunto + (pesoDoc * pesoCon)
            sumaNormaVect = sumaNormaVect + (pesoDoc * pesoDoc)
        raizSumaNormaVect = math.sqrt(sumaNormaVect)
        return sumaProductoPunto, raizSumaNormaVect

    def sumaVector(self, dictVec):
        suma = 0.0
        for word in sorted(dictVec.keys()):
            suma = suma + dictVec[word]
        return suma

    def normaVector(self, dictVec):
        norma = dict()
        for word in sorted(dictVec.keys()):
            valVector = dictVec[word]
            norma[word] = valVector * valVector
        return norma

    def productoPuntoTodosVectores(self, docs, vectorConsulta):
        sumaProductoPunto = dict()
        raizSumaNormaVect = dict()
        for doc in sorted(docs.keys()):
            dictPesosDoc = docs[doc]
            sumaProductoPuntoYraizSumaNormaVect = self.productoPunto(dictPesosDoc, vectorConsulta)
            sumaProductoPunto[doc] = sumaProductoPuntoYraizSumaNormaVect[0]
            raizSumaNormaVect[doc] = sumaProductoPuntoYraizSumaNormaVect[1]
        return sumaProductoPunto, raizSumaNormaVect

    def sumaTodosVectores(self, docs):
        docsSumados = dict()
        for doc in sorted(docs.keys()):
            dictPesosDoc = docs[doc]
            suma = self.sumaVector(dictPesosDoc)
            docsSumados[doc] = suma
        return docsSumados

    def normaTodosVectores(self, docs):
        docsNorma = dict()
        for doc in sorted(docs.keys()):
            dictPesosDoc = docs[doc]
            normaVector = self.normaVector(dictPesosDoc)
            docsNorma[doc] = normaVector
        return docsNorma

    def raizTodosVectores(self, docs):
        docsRaiz = dict()
        for doc in sorted(docs.keys()):
            suma = docs[doc]
            docsRaiz[doc] = math.sqrt(suma)
        return docsRaiz

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
        dicWtd = weights.getDicWtd()
        vectPeso = agregar_terminos_que_no_tenga(dicVoc, dicWtd)
        dicWts[nombreDoc] = vectPeso
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

@cross_origin()
@app.route('/<consulta>')
def consulta(consulta):
    inicio = time()
    vectConsulta = procConsultas.generar_vector_consulta(consulta)
    docsPesos = procConsultas.buscaDocumentosRealacionados(dictIndice, linesPonsting, wtdTodos)
    sumaProductoPuntoYraizSumaNormaVect = procConsultas.productoPuntoTodosVectores(docsPesos,vectConsulta)
    docsProductoPuntoSumado = sumaProductoPuntoYraizSumaNormaVect[0]
    docsNormaSumadosRaiz = sumaProductoPuntoYraizSumaNormaVect[1]
    consultaNormaSumadaRaiz = procConsultas.sqrtconsultaNormaSumada(vectConsulta)
    similaridad = procConsultas.similaridad(docsProductoPuntoSumado, docsNormaSumadosRaiz, consultaNormaSumadaRaiz)
    ranking = sorted(similaridad.items(), key=operator.itemgetter(1))
    lista = list()
    largo = ranking.__len__()
    for x in range(0, largo):
        posActual = largo - x - 1
        nombreDocumento = str(ranking[posActual][0])
        linkDocumento = urlsDict[ranking[posActual][0]]
        string = docsProcesados[nombreDocumento]
        resu = '...'
        for word in procConsultas.words:
            index = string.lower().find(' '+ word +' ')
            if index >= 0:
                if index < 30:
                    index = 30
                resu = resu + string[index-30:index+40] + "..."
        lista.append(Documento(nombreDocumento, linkDocumento, resu))
    fin = time() - inicio
    print("FIN: %.10f seconds." % fin)
    retornoDocumentos = Documentos(lista, lista.__len__(), fin)
    jsonStringTodo = json.dumps(retornoDocumentos, default=lambda o: o.__dict__, indent=4)
    return jsonStringTodo

@cross_origin()
@app.route('/pagina/<nombreDoc>')
def getPagina(nombreDoc):
    print(nombreDoc)
    htmlReader = HTMLReader((nombreDoc+'.html').encode('utf-8-sig'))
    string = htmlReader.getHtml()
    return string

@cross_origin()
@app.route('/like/<consulta>')
def getLike(consulta):
    consulta = json.loads(consulta)
    inicio = time()
    weights = Weights()
    vectConsulta = procConsultas.generar_vector_consulta(consulta['q'])
    for x in range(0,len(consulta['docs'])):
        weightDoc=weights.getDicWeightsConsulta(consulta['docs'][x])
        for key, value in weightDoc.items():
            vectConsulta[key] += (1/len(consulta['docs']))*value
    docsPesos = procConsultas.buscaDocumentosRealacionados(dictIndice, linesPonsting, wtdTodos)
    sumaProductoPuntoYraizSumaNormaVect = procConsultas.productoPuntoTodosVectores(docsPesos,vectConsulta)
    docsProductoPuntoSumado = sumaProductoPuntoYraizSumaNormaVect[0]
    docsNormaSumadosRaiz = sumaProductoPuntoYraizSumaNormaVect[1]
    consultaNormaSumadaRaiz = procConsultas.sqrtconsultaNormaSumada(vectConsulta)
    similaridad = procConsultas.similaridad(docsProductoPuntoSumado, docsNormaSumadosRaiz, consultaNormaSumadaRaiz)
    ranking = sorted(similaridad.items(), key=operator.itemgetter(1))
    lista = list()
    largo = ranking.__len__()
    for x in range(0, largo):
        posActual = largo - x - 1
        nombreDocumento = str(ranking[posActual][0])
        linkDocumento = urlsDict[ranking[posActual][0]]
        string = docsProcesados[nombreDocumento]
        resu = '...'
        for word in procConsultas.words:
            index = string.lower().find(' '+ word +' ')
            if index >= 0:
                if index < 30:
                    index = 30
                resu = resu + string[index-30:index+40] + "..."
        lista.append(Documento(nombreDocumento, linkDocumento, resu))
    fin = time() - inicio
    print("FIN: %.10f seconds." % fin)
    retornoDocumentos = Documentos(lista, lista.__len__(), fin)
    jsonStringTodo = json.dumps(retornoDocumentos, default=lambda o: o.__dict__, indent=4)
    return jsonStringTodo

if __name__ == '__main__':
    app.run()