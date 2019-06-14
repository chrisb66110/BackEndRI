class HTMLReader:
    def __init__(self, docName):
        docName = str(docName, 'utf-8-sig')
        self.fileName = './Coleccion/' + docName
        # Se tiene que cambiar el tipo de encoding del archivo y
        # se tiene que ignorar ciertos errores de caracteres que dice que no existen.
        self.file = open(self.fileName, "rb")


    # Metodo que devuelve todito el html del archivo
    def getHtml(self):
        html = self.file.read().decode("ISO-8859-1")
        return html
