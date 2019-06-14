from flask import Flask

from Rules import *
from DocWordCounter import *
from URLsReader import *
from Frecuencias import *
from Weights import *
#from Indice import *
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
        for term in vect.keys():
            print(term + ': ' + str(vect[term]))

procConsultas = ProcConsultas()
@app.route('/<consulta>')
def hello_world(consulta):
    procConsultas.generar_vector_consulta(consulta)

    return consulta

if __name__ == '__main__':
    app.run()
