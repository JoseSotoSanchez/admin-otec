from django.db import models

class Contacto(models.Model):
    id = models.AutoField(primary_key=True)
    nombre = models.TextField(null=True, verbose_name = "Nombre")
    correo = models.TextField(null=True, verbose_name = "Correo")
    telefono = models.TextField(null=True, verbose_name = "Telefono")
    motivo = models.TextField(null=True, verbose_name = "Motivo")
    mensaje = models.TextField(null=True, verbose_name = "Mensaje")
    fecha = models.DateTimeField()

    class Meta:
        db_table = "Contacto"

class Dias(models.Model):
    id = models.AutoField(primary_key=True)
    rango = models.TextField(verbose_name = "Rango")

    class Meta:
        db_table = "Dias"

class Horario(models.Model):
    id = models.AutoField(primary_key=True)
    rango = models.TextField(verbose_name = "Rango")

    class Meta:
        db_table = "Horario"

class Curso(models.Model):
    id = models.AutoField(primary_key=True)
    nombre = models.TextField(null=True, verbose_name = "Nombre")
    codigo_curso = models.TextField(null=True, verbose_name = "Codigo Curso")
    fecha_inicio = models.DateTimeField()
    fecha_fin = models.DateTimeField()
    id_dias = models.ForeignKey(Dias, db_column='id_dias', on_delete=models.CASCADE)
    id_horario = models.ForeignKey(Horario, db_column='id_horario', on_delete=models.CASCADE)
    costo = models.IntegerField(verbose_name = "Costo")
    modalidad = models.TextField(null=True, verbose_name = "Modalidad")
    activo = models.IntegerField(null=True, verbose_name = "Activo")

    class Meta:
        db_table = "Curso"

class Estado_Alumno(models.Model):
    id = models.AutoField(primary_key=True)
    estado = models.TextField(verbose_name = "Estado")

    class Meta:
        db_table = "Estado_Alumno"


class LogUsuario(models.Model):
    id = models.AutoField(primary_key=True)
    nick = models.TextField(null=True, verbose_name = "Nick")
    clave = models.TextField(null=True, verbose_name = "Clave")
    fecha = models.DateTimeField(null=True, verbose_name = "Fecha")
    estado = models.TextField(null=True, verbose_name = "Estado")
    ip = models.TextField(null=True, verbose_name = "Ip")
    curso = models.TextField(null=True, verbose_name = "Curso")
    idAlumno = models.IntegerField(null=True, verbose_name = "id alumno generado")

    class Meta:
        db_table = "LogUsuario"

class Subsidio(models.Model):
    id = models.AutoField(primary_key=True)
    porcentaje = models.TextField(verbose_name = "Porcentaje")

    class Meta:
        db_table = "Subsidio"

class Usuario(models.Model):
    id = models.AutoField(primary_key=True)
    nombre = models.TextField(verbose_name = "Nombre")
    nick = models.TextField(verbose_name = "Nick")
    clave = models.TextField(null=True, verbose_name = "Clave")
    correo = models.TextField(null=True, verbose_name = "Correo")
    numero = models.TextField(null=True, verbose_name = "Numero")
    activo = models.IntegerField(null=True, verbose_name = "Activo")

    class Meta:
        db_table = "Usuario"

class Alumno(models.Model):
    id = models.AutoField(primary_key=True, verbose_name = "")
    nombre = models.TextField(verbose_name = "Nombre")
    apellido = models.TextField(verbose_name = "Apellido")
    rut = models.TextField(verbose_name = "Rut") 
    sexo = models.TextField(null=True, verbose_name = "Sexo")
    edad = models.TextField(null=True, verbose_name = "Edad")
    nacionalidad = models.TextField(verbose_name = "Nacionalidad")  
    estado_civil = models.TextField(null=True, verbose_name = "Estado Civil")
    email = models.TextField(verbose_name = "Email")
    telefono = models.TextField(verbose_name = "Telefono")
    profesion = models.TextField(null=True, verbose_name = "Profesion")  
    nivel_estudios = models.TextField(null=True, verbose_name = "Nivel de estudios")
    situacion_laboral  = models.TextField(null=True, verbose_name = "Situacion Laboral")
    direccion = models.TextField(null=True, verbose_name = "Direccion")
    region = models.TextField(null=True, verbose_name = "Region")
    fecha = models.DateTimeField(null=True, verbose_name = "Fecha Postulacion")
    id_curso = models.ForeignKey(Curso, db_column='id_curso',on_delete=models.CASCADE)
    id_subsidio = models.ForeignKey(Subsidio, db_column='id_subsidio',on_delete=models.CASCADE)
    ingreso = models.TextField(verbose_name = "Ingreso")

    class Meta:
        db_table = "Alumno"

class Pagos(models.Model):
    id = models.AutoField(primary_key=True)
    id_alumno = models.ForeignKey(Alumno, db_column='id_alumno', on_delete=models.CASCADE)
    id_curso = models.ForeignKey(Curso, db_column='id_curso', on_delete=models.CASCADE)
    monto = models.IntegerField(null=True, verbose_name = "Monto")
    medio_pago = models.TextField(null=True, verbose_name = "Medio de pago")
    fecha = models.DateTimeField(null=True, verbose_name = "Fecha")

    class Meta:
        db_table = "Pagos"
    
class Alumno_Estado(models.Model):
    id = models.AutoField(primary_key=True)
    id_estado = models.ForeignKey(Estado_Alumno, db_column='id_estado', on_delete=models.CASCADE)
    id_alumno = models.ForeignKey(Alumno, db_column='id_alumno', on_delete=models.CASCADE)
    fecha = models.DateTimeField(null=True, verbose_name = "Fecha Estado")
    id_usuario = models.IntegerField(null=True, verbose_name = "Id Usuario")

    class Meta:
        db_table = "Alumno_Estado"
    
class AlumnoView(models.Model):
    id = models.AutoField(primary_key=True, verbose_name = "")
    nombre = models.TextField(verbose_name = "Nombre")
    apellido = models.TextField(verbose_name = "Apellido")
    rut = models.TextField(verbose_name = "Rut") 
    sexo = models.TextField(null=True, verbose_name = "Sexo")
    edad = models.TextField(null=True, verbose_name = "Edad")
    nacionalidad = models.TextField(verbose_name = "Nacionalidad")  
    estado_civil = models.TextField(null=True, verbose_name = "Estado Civil")
    email = models.TextField(verbose_name = "Email")
    telefono = models.TextField(verbose_name = "Telefono")
    profesion = models.TextField(null=True, verbose_name = "Profesion")  
    nivel_estudios = models.TextField(null=True, verbose_name = "Nivel de estudios")
    situacion_laboral  = models.TextField(null=True, verbose_name = "Situacion Laboral")
    direccion = models.TextField(null=True, verbose_name = "Direccion")
    region = models.TextField(null=True, verbose_name = "Region")
    fecha = models.DateTimeField(null=True, verbose_name = "Fecha Postulacion")
    id_curso = models.ForeignKey(Curso, db_column='id_curso', on_delete=models.CASCADE)
    id_subsidio = models.ForeignKey(Subsidio, db_column='id_subsidio', on_delete=models.CASCADE)
    ingreso = models.TextField(verbose_name = "Ingreso")

    class Meta:
        managed = False  # es una vista
        db_table = 'alumno_view' 
