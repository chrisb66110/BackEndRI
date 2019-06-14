class FileGenerator:
    numberCharacteresTerm = 30
    numberCharacteresFreq = 12
    numberCharacteresFreqNorm = 20
    numberCharacteresNumberDocument = 12
    numberCharacteresFreqInv = 20
    numberCharacteresWeight = 20
    numberCharacteresAlias = 30
    numberCharacteresPosInitial = 12
    numberCharacteresEntrys = 12

    # Funcion para rellenar espacios para que la hilera string quede de numberCharacteres de caracteres
    def formatNumberCharacters(self, numberCharacteres, string):
        formato = '{:<'+str(numberCharacteres)+'}'
        return formato.format(string)

    # Funcion para convertir numero a caracteres
    def formatNnumberToString(self, numberCharacteres, number):
        return self.formatNumberCharacters(numberCharacteres,str(number))

    # Funcion que crea una linea del archivo .tok
    def lineTok(self, term, freq, freqNorm):
        return self.formatNumberCharacters(self.numberCharacteresTerm, term) + ' ' + self.formatNnumberToString(self.numberCharacteresFreq,freq) + ' ' + self.formatNnumberToString(self.numberCharacteresFreqNorm, freqNorm)+'\n'

    # Metodo que generar archivo .tok
    # 30 caracteres para el termino
    # 1 espacio
    # 12 espacios para la frecuencia
    # 1 espacio
    # 20 espacios para la frecuencia normalizada
    def tokGenerate(self, fileName, dictFreq, dictFreqNorm):
        fileSave = './DocumentosProcesados/tok/' + fileName + '.tok'
        file = open(fileSave, 'w')
        for word in sorted(dictFreq.keys()):
            file.write(self.lineTok(word, dictFreq[word], dictFreqNorm[word]))
        print(fileName + ".tok generado")

    # Funcion que crea una linea del archivo vocabulario
    def lineVocabulary(self, term, numberDocument, freqInv):
        return self.formatNumberCharacters(self.numberCharacteresTerm, term) + ' ' + self.formatNnumberToString(
            self.numberCharacteresNumberDocument, numberDocument) + ' ' + self.formatNnumberToString(self.numberCharacteresFreqInv,
                                                                                     freqInv)+'\n'
    # Metodo que genera el archivo vocabulario
    # 30 caracteres termino
    # 1 espacio
    # 12 espacios para el numero de documentos en que aparece el termino
    # 1 espacio en blanco
    # 20 caracteres para la frecuencia inversa
    def vocabularyGenerate(self, fileName, dictFreq):
        fileSave = './DocumentosProcesados/vocabulario/' + fileName + '.txt'
        file = open(fileSave, 'w')
        for word in sorted(dictFreq.keys()):
            file.write(self.lineVocabulary(word, dictFreq[word].getNumDocs(), dictFreq[word].getFrecInversa()))
        print("vocabulario.txt generado")

    # Funcion que crea una linea del archivo .wtd
    def lineWtd(self, term, peso):
        return self.formatNumberCharacters(self.numberCharacteresTerm, term) + ' ' + self.formatNnumberToString(
            self.numberCharacteresWeight, peso) + '\n'

    # Metodo que genera el archivo .wtd
    # 30 caracteres termino
    # 1 espacio
    # 20 espacios para el peso del termino en el documento
    def wtdGenerate(self, fileName, dictWeight):
        fileSave = './DocumentosProcesados/wtd/' + fileName + '.wtd'
        file = open(fileSave, 'w')
        for word in sorted(dictWeight.keys()):
            file.write(self.lineWtd(word, dictWeight[word]))
        print(fileName + ".wtd generado")

    # Funcion que crea una linea del archivo postings
    def linePostings(self, term, alias, peso):
        return self.formatNumberCharacters(self.numberCharacteresTerm, term) + ' ' + \
               self.formatNumberCharacters(self.numberCharacteresAlias, alias) + ' ' + \
               self.formatNnumberToString(self.numberCharacteresWeight, peso) + '\n'

    # Metodo que genera el archivo postings
    # 30 caracteres termino
    # 1 espacio
    # 30 espacios para el alias del archivo
    # 1 espacio en blanco
    # 20 espacios para el peso del termino en el documento
    def postingsGenerate(self, fileName, dictWeight):
        fileSave = './DocumentosProcesados/postings/' + fileName + '.txt'
        file = open(fileSave, 'w')
        for wordFile in sorted(dictWeight.keys()):
            file.write(self.linePostings(wordFile[0], wordFile[1], dictWeight[wordFile]))
        print(fileName + ".txt generado")

    # Funcion que crea una linea del archivo indice
    def lineIndice(self, term, posInitial, entrys):
        return self.formatNumberCharacters(self.numberCharacteresTerm, term) + ' ' + \
               self.formatNumberCharacters(self.numberCharacteresPosInitial, posInitial) + ' ' + \
               self.formatNnumberToString(self.numberCharacteresEntrys, entrys) + '\n'

    # Metodo que genera el archivo indice
    # 30 caracteres termino
    # 1 espacio
    # 12 espacios para la posición inicial dentro del archivo postings (numero de linea).
    # 1 espacio en blanco
    # 12 espacios para la cantidad de entradas dentro del archivo de Postings (el número de documentos donde aparece).
    def indiceGenerate(self, fileName, dictPositngs):
        fileSave = './DocumentosProcesados/indice/' + fileName + '.txt'
        file = open(fileSave, 'w')
        for word in sorted(dictPositngs.keys()):
            file.write(self.linePostings(word, dictPositngs[word][0], dictPositngs[word][1]))
        print(fileName + ".txt generado")