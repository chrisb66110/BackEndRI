class URLsReader:
    def __init__(self):
        # Se tiene que cambiar el tipo de encoding del archivo y
        # se tiene que ignorar ciertos errores de caracteres que dice que no existen.
        self.file = open('./URLs.txt', "rb")

    # Metodo utilizado para obtener el titulo de los archivos.
    def getTitle(self):
        linea = self.file.readline()
        titulo = linea.split()
        if titulo:
            # Se quita el caracter '\ufeff' ya que es parte
            # del BOM del encoding del documento que se metia en los strings.
            retValue = titulo[0] # Devuelve el titulo nada mas, por ahora el URL no nos interesa.
        else:
            retValue = None       # Manera contraria devuelve un null para que la otra clase lo maneje.
        return retValue

    def closeFile(self):
        self.file.close()

