import configparser
import os

class Configuracion:
    def __init__(self, archivo='config.properties'):
        self.archivo = archivo
        self.config = configparser.ConfigParser()
        
        # Verificar si el archivo existe y cargar la configuración
        if os.path.exists(self.archivo):
            self.config.read(self.archivo)

    def obtener(self, clave):
        """Obtener el valor de una clave específica."""
        return self.config.get('DEFAULT', clave, fallback=None)

    def establecer(self, clave, valor):
        """Establecer el valor de una clave específica."""
        if 'DEFAULT' not in self.config:
            self.config['DEFAULT'] = {}
        
        self.config['DEFAULT'][clave] = valor
        
        # Guardar los cambios en el archivo
        with open(self.archivo, 'w') as f:
            self.config.write(f)