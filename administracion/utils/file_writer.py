import os

class FileWriter():
  """Esta clase recibe un nombre de archivo y contenido para generar otro archivo el cual será generado por defecto en la ruta /admin/config/*.
  """
  def __init__(self, file_name, content):
    """Constructor que instancia un objeto con los atributos file_name y content.

    Args:
        file_name (str): nombre del archivo (preferir extenciónes .txt)
        content (str): contenido que irá al interior del archivo
    """
    self.file_name = file_name
    self.content = content

  def __str__(self):
    return f"Nombre del archivo: {self.file_name}\nContenido a escribir: {self.content}"

  def __get_file_path(self):
    """Encuentra la ruta absoluta (desde la raiz del sistema) hasta la carpeta config. Luego concatena el nombre del archivo especificado
    al momento de instanciar el objeto.
    """
    path = os.getcwd()
    path_data = os.path.join(path, "config", self.file_name)
    self.file_path = path_data
    print("Ruta del archivo a escribir: ", self.file_path)

  def write_new_content(self):
    """Sobreescribe o escribe la nueva información en el archivo.
    """
    self.__get_file_path()
    f = open(self.file_path, "w")
    f.write(self.content)
    f.close()