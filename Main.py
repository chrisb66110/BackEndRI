from Rules import *
from DocWordCounter import *
from URLsReader import *
from HTMLReader import *
from Frecuencias import *
from Postings import *
from Weights import *
from Indice import *

def main():
    urlDoc = URLsReader()
    rules = Rules()
    title = urlDoc.getTitle()
    freq = Frecuencias()
    generador = FileGenerator()
    filesName = []
    while(title is not None):
        fileName = re.sub('.html', '', str(title, 'utf-8-sig'))
        filesName.append(fileName)
        html = HTMLReader(title)
        # Obtiene tod o el HTML del documento.
        htmlString = html.getHtml()
        # Devuelve en un string todas las palabras del documento
        words = rules.applyRules(htmlString)
        # Se crea el objeto DocWord que se envia el titulo del archivo y el string de palabras
        docWordCount =  DocWordCounter(html, words)
        # Separa las palabras y las agrega en un diccionario por cada documento.
        docWordCount.generateStopWordsDict()
        docWordCount.separateWords()
        wordDict = docWordCount.generateDict()
        # Tiene el diccionario con las frecuencias normalizadas de cada palabra por documento.
        freqDict = freq.generateFrequency(wordDict)
        # Obtiene el siguiente Documento de HTML
        title = urlDoc.getTitle()
        # Genera el .tok
        generador.tokGenerate(fileName, wordDict, freqDict)
    # Genera el diccionario para obtener los datos para el vocabulario.
    freqInv = freq.generateVocabDic()
    generador.vocabularyGenerate('vocabulario', freqInv)
    # Genera los archivos awt
    weights = Weights()
    weights.generateWtd(filesName)
    # Genera el archivo postings
    postings = Postings()
    postings.generatePostings(filesName)
    # Genera el archivo indice
    indice = Indice()
    indice.generateIndice()

if __name__ == '__main__':
    main()