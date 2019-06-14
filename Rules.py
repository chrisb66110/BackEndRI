import re
from unicodedata import normalize

# Clase para implementar las reglas que se va a utilizar
class Rules:
    maxLength = 30

    #Regla para eliminar las etiquetas html
    def removeTagsHTML(self, stringDoc):
        return re.sub(r'<[^>]*?>', ' ', stringDoc)

    def removeComments(self, stringDoc):
        return re.sub(r'(/\*(.|\n)*?\*/|<!--(.*\n*)*-->)', ' ', stringDoc)

    def removeNbsp(self, stringDoc):
        return re.sub(r'&nbsp;', ' ', stringDoc)

    def removeCSS(self, stringDoc):
        return re.sub(r'(?s)<style>(.*?)<\/style>', ' ', stringDoc)

    #Regla para eliminar palabras de mas de 30 caracteres
    def removeMaxLength(self, stringDoc):
        return re.sub(r'[^> ]{30,}', ' ', stringDoc)

    #Regla para pasar el texto a minuscula
    def toLowerCase(self, stringDoc):
        return stringDoc.lower()

    #Regla para quitar caracteres que no sean a-z, A-Z, 0-9, _
    def removeCharactersInvalid(self, stringDoc):
        return re.sub(r'[A-Za-z0-9]*[!@#$%^&*(),.?":;{}|\\<>\[\]][\w]*', ' ', stringDoc)

    #Regla para quitar tildes
    def removeTick(self, stringDoc):
        return normalize('NFC',
                         re.sub(r"([^n\u0300-\u036f]|ñ(?!\u0303(?![\u0300-\u036f])))[\u0300-\u036f]+",
                                r"\1",
                                normalize("NFD", stringDoc),
                                0,
                                re.I)
                         )

    def changeTick(selfs, stringDoc):
        docChangeTick = stringDoc.replace('&aacute;', 'a')
        docChangeTick = docChangeTick.replace('&Aacute;', 'a')
        docChangeTick = docChangeTick.replace('&eacute;', 'e')
        docChangeTick = docChangeTick.replace('&Eacute;', 'e')
        docChangeTick = docChangeTick.replace('&iacute;', 'i')
        docChangeTick = docChangeTick.replace('&Iacute;', 'i')
        docChangeTick = docChangeTick.replace('&oacute;', 'o')
        docChangeTick = docChangeTick.replace('&Oacute;', 'o')
        docChangeTick = docChangeTick.replace('&uacute;', 'u')
        docChangeTick = docChangeTick.replace('&Uacute;', 'u')
        docChangeTick = docChangeTick.replace('&ntilde;', 'n')
        docChangeTick = docChangeTick.replace('&Ntilde;', 'n')
        return docChangeTick

    #Regla para eliminar palabras que son alfanumericas
    def removeIfStartWithNumber(self, stringDoc):
        #Hay que dejar ese espacio al final para que indique que es hasta que finalizo la palabra
        return re.sub(r'[\d]+[a-zA-Z_]+? ', ' ', stringDoc)

    #Regla para dejar los numeros hasta el 999,999
    def removeNumberBiggerThan(self, stringDoc):
        return re.sub(r'[\d]{7,}(,[\d]+)?', ' ', stringDoc)

    def removeWhiteSpace(self, stringDoc):
        return re.sub(r'\s+', ' ', stringDoc)

    def removeEnters(self, stringDoc):
        return re.sub(r'\r?\n|\r|\n', ' ', stringDoc)

    def removePunctuation(self, stringDoc):
        return re.sub(r'[.,!?¿¡;\-:/“”`\']', ' ', stringDoc)

    def removeStyle(self, stringDoc):
        return re.sub(r'(?s)<style(.*?)>(.*?)<\/style>', ' ', stringDoc)

    def removeScript(self, stringDoc):
        return re.sub(r'(?s)<script(.*?)>(.*?)<\/script>', ' ', stringDoc)

    def removeLastPass(self, stringDoc):
        return re.sub(r'(?![\sA-Za-za-z0-9]).*', ' ', stringDoc)

    def applyRules(self, stringDoc):
        stringDoc = self.toLowerCase(stringDoc)
        stringDoc = self.removeStyle(stringDoc)
        stringDoc = self.removeScript(stringDoc)
        stringDoc = self.removeTagsHTML(stringDoc)
        stringDoc = self.removeComments(stringDoc)
        stringDoc = self.removeNbsp(stringDoc)
        stringDoc = self.changeTick(stringDoc)
        stringDoc = self.removePunctuation(stringDoc)
        stringDoc = self.removeEnters(stringDoc)
        stringDoc = self.removeCSS(stringDoc)
        stringDoc = self.removeMaxLength(stringDoc)
        stringDoc = self.removeCharactersInvalid(stringDoc)
        stringDoc = self.removeTick(stringDoc)
        stringDoc = self.removeIfStartWithNumber(stringDoc)
        stringDoc = self.removeNumberBiggerThan(stringDoc)
        stringDoc = self.removeLastPass(stringDoc)
        stringDoc = self.removeWhiteSpace(stringDoc)
        return stringDoc
