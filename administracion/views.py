from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.template import loader
from django.db import transaction
from django.core.exceptions import ValidationError
from django.views.decorators.csrf import csrf_exempt
from django.db import connection
from datetime import datetime
import locale
from .services import obtener_aspirantes_por_curso, obtener_cursos
from administracion.models import AlumnoView , Alumno, Curso#, Proveedor, Pedido, Stock, ProductoDetalle, PedidoProducto, OrdenVenta, Venta, PedidosTableView, PedidosProductosView, TipoSalida, ProductoSalidaInventario, SalidaInventario, ProductoDetalleStockView, StockResumenPedidosView
from .utils.file_writer import FileWriter
from abc import abstractmethod
from datetime import datetime, date
from pathlib import Path
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils import timezone
from django.views.decorators.http import require_POST
from django.urls import reverse
from openpyxl import Workbook
from io import BytesIO
from urllib.parse import urlencode
import bcrypt

from administracion.models import (
    AlumnoView,
    Alumno,
    Curso,
    Dias,
    Horario,
    Pagos,
    Usuario,
    Alumno_Estado,
    Estado_Alumno,
    LogUsuario,
)

from .services import (
    obtener_aspirantes_por_curso,
    obtener_cursos,
    obtener_cursos_detalle,
    obtener_alumnos_correo_bienvenida,
    obtener_estados_alumno,
    obtener_pagos_alumno,
    obtener_dashboard_resumen,
    obtener_ultimos_alumnos_dashboard,
    obtener_cursos_activos_dashboard,
    obtener_alumnos_por_curso_activo,
    obtener_alumnos_por_horario,
    obtener_resumen_cursos_activos_dashboard,
)

from .emails import (
    enviar_email_bienvenida,
    enviar_email_aceptacion,
    enviar_email_pago,
    enviar_email_bienvenida_especial,
)
import json

#Clase generica para la tabla generica 
class ViewCustom:
    @staticmethod
    def get_atributos(modelo): 
        return [field.verbose_name for field in modelo._meta.fields]
    
    @staticmethod
    def get_ids(modelo): 
        return [field.name for field in modelo._meta.fields]
    
    @abstractmethod
    def get_context_base(self):
        pass


 
class AuthView:

    @staticmethod
    def login(request):

        # Si ya está conectado, no mostramos login nuevamente
        if request.session.get("loggedin"):
            return redirect("dashboard")

        if request.method == "POST":

            usuario_ingresado = request.POST.get(
                "usuario",
                ""
            ).strip()

            clave_ingresada = request.POST.get(
                "clave",
                ""
            )

            if not usuario_ingresado or not clave_ingresada:

                messages.error(
                    request,
                    "Debe ingresar usuario y contraseña."
                )

                return render(
                    request,
                    "administracion/login.html"
                )

            try:

                usuario = Usuario.objects.filter(
                    nick=usuario_ingresado
                ).first()

                login_correcto = False

                if usuario and usuario.clave:

                    try:

                        login_correcto = bcrypt.checkpw(
                            clave_ingresada.encode("utf-8"),
                            usuario.clave.encode("utf-8")
                        )

                    except (ValueError, TypeError):
                        login_correcto = False


                # ============================================
                # LOGIN CORRECTO
                # ============================================

                if login_correcto:

                    # Si activo = 0, no permitimos acceso
                    if usuario.activo == 0:

                        AuthView._registrar_log(
                            request,
                            usuario_ingresado,
                            "Usuario inactivo"
                        )

                        messages.error(
                            request,
                            "El usuario se encuentra desactivado."
                        )

                        return render(
                            request,
                            "administracion/login.html"
                        )


                    # Limpiar cualquier sesión anterior
                    request.session.flush()


                    # Mismas variables que usaba Flask
                    request.session["loggedin"] = True
                    request.session["id"] = usuario.id
                    request.session["usuario"] = usuario.nick
                    request.session["nombre"] = usuario.nombre


                    # Sesión válida por 8 horas
                    request.session.set_expiry(
                        60 * 60 * 8
                    )


                    AuthView._registrar_log(
                        request,
                        usuario.nick,
                        "OK"
                    )


                    messages.success(
                        request,
                        f"Bienvenido(a), {usuario.nombre}."
                    )


                    return redirect(
                        "dashboard"
                    )


                # ============================================
                # LOGIN INCORRECTO
                # ============================================

                AuthView._registrar_log(
                    request,
                    usuario_ingresado,
                    "fallido"
                )


                messages.error(
                    request,
                    "Usuario y/o contraseña incorrectos."
                )


            except Exception as e:

                messages.error(
                    request,
                    f"Error al iniciar sesión: {str(e)}"
                )


        return render(
            request,
            "administracion/login.html"
        )


    @staticmethod
    def logout(request):

        request.session.flush()

        return redirect(
            "login"
        )


    @staticmethod
    def _registrar_log(
        request,
        nick,
        estado
    ):

        try:

            ip = request.META.get(
                "REMOTE_ADDR",
                ""
            )

            LogUsuario.objects.create(
                nick=nick,

                # No guardamos contraseña ni derivados
                # de la contraseña ingresada.
                clave=None,

                fecha=timezone.now(),
                estado=estado,
                ip=ip,
                curso=None,
                idAlumno=None,
            )

        except Exception as e:

            # Un fallo del log no debe impedir iniciar sesión
            print(
                f"Error registrando login: {e}"
            )
# Para generar la vista con la tabla si o si debe existir el modelo (usen el verbose)
class AlumnoView(ViewCustom):

    @staticmethod
    def alumnos(request):

        cursos = obtener_cursos()
        estados = obtener_estados_alumno()

        curso_id = (
            request.POST.get("id_curso")
            if request.method == "POST"
            else request.GET.get("curso")
        )

        alumnos = []

        if curso_id:
            alumnos = obtener_aspirantes_por_curso(
                curso_id
            )

        context = {

            "cursos": cursos,

            "curso_id":
                int(curso_id)
                if curso_id
                else None,

            "title": "Aspirantes",

            "actions_bar":
                "administracion/actions_bar/alumnos.html",

            "row_actions":
                "administracion/row_actions/alumnos.html",

            "table_order": "desc",

            "ids": [
                "id",
                "id_curso",
                "id_estado_alumno",
            ],

            "mostrar_estado_alumno": True,
            
            "atributos": [
                "id",
                "nombre",
                "apellido",
                "rut",
                "email",
                "telefono",
                "estado",
                "modificado_por",
                "total_pagos",
            ],

            "data": alumnos,

            "estados": estados,

            "total": len(alumnos),
            
        }

        return render(
            request,
            "administracion/alumnos.html",
            context
        )


    # ============================================
    # MODIFICAR ALUMNO + ESTADO
    # ============================================

    @staticmethod
    @require_POST
    @transaction.atomic
    def actualizar_alumno(request, alumno_id):

        curso_id = request.POST.get("curso_id")
        pagina = request.POST.get("pagina", "0")
        origen = request.POST.get(
            "origen",
            "alumnos"
        )
        try:

            alumno = get_object_or_404(
                Alumno,
                id=alumno_id
            )

            estado_id = request.POST.get("estado")

            nombre = request.POST.get("nombre")
            apellido = request.POST.get("apellido")
            email = request.POST.get("email")
            telefono = request.POST.get("telefono")

            if not estado_id:
                raise Exception(
                    "Debe seleccionar un estado."
                )

            # ==========================================
            # ACTUALIZAR DATOS DEL ALUMNO
            # ==========================================

            alumno.nombre = nombre
            alumno.apellido = apellido
            alumno.email = email
            alumno.telefono = telefono

            alumno.save(
                update_fields=[
                    "nombre",
                    "apellido",
                    "email",
                    "telefono",
                ]
            )

            # ==========================================
            # INSERTAR NUEVO ESTADO
            # ==========================================
            #
            # Por ahora usamos usuario 1.
            # Cuando migremos correctamente el login,
            # lo reemplazamos por el usuario conectado.
            #

            Alumno_Estado.objects.create(
                id_estado_id=int(estado_id),
                id_alumno=alumno,
                fecha=timezone.now(),
                id_usuario = request.session["id"],
            )

            messages.success(
                request,
                "Aspirante actualizado correctamente."
            )

        except Exception as e:

            messages.error(
                request,
                f"Error al actualizar aspirante: {str(e)}"
            )

        return AlumnoView._redirect_alumnos(
            curso_id,
            pagina,
            origen
        )

    # ============================================
    # REGISTRAR PAGO
    # ============================================

    @staticmethod
    @require_POST
    @transaction.atomic
    def guardar_pago(request, alumno_id):

        curso_id = request.POST.get(
            "curso_id"
        )

        pagina = request.POST.get(
            "pagina",
            "0"
        )
        origen = request.POST.get(
            "origen",
            "alumnos"
        )
        try:

            monto = request.POST.get(
                "monto"
            )

            medio_pago = request.POST.get(
                "medio_pago"
            )

            if not monto or not medio_pago:
                raise Exception(
                    "Debe ingresar monto y forma de pago."
                )

            alumno = get_object_or_404(
                Alumno,
                id=alumno_id
            )

            curso = get_object_or_404(
                Curso,
                id=curso_id
            )

            Pagos.objects.create(
                id_alumno=alumno,
                id_curso=curso,
                monto=int(monto),
                medio_pago=medio_pago,
                fecha=timezone.now(),
            )

            # Por ahora usamos usuario 1.
            # Cuando migremos correctamente el login,
            # se reemplaza por el usuario autenticado.
            Alumno_Estado.objects.create(
                id_estado_id=18,
                id_alumno=alumno,
                fecha=timezone.now(),
                id_usuario = request.session["id"],
            )

            messages.success(
                request,
                "Pago guardado correctamente."
            )

        except Exception as e:

            messages.error(
                request,
                f"Error al guardar pago: {str(e)}"
            )

        return AlumnoView._redirect_alumnos(
            curso_id,
            pagina,
            origen
        )


    # ============================================
    # PAGOS REALIZADOS
    # ============================================

    @staticmethod
    def pagos(request, alumno_id, curso_id):

        alumno = get_object_or_404(
            Alumno,
            id=alumno_id
        )

        curso = get_object_or_404(
            Curso,
            id=curso_id
        )

        pagos = obtener_pagos_alumno(
            alumno_id,
            curso_id
        )

        total = sum(
            pago["monto"] or 0
            for pago in pagos
        )

        context = {

            "title": "Pagos realizados",

            "alumno": alumno,

            "curso": curso,

            "pagos": pagos,

            "total": total,
        }

        return render(
            request,
            "administracion/pagos_alumno.html",
            context
        )


    # ============================================
    # EXPORTAR TODOS
    # ============================================

    @staticmethod
    @require_POST
    def exportar_alumnos(request, curso_id):

        alumnos = obtener_aspirantes_por_curso(
            curso_id
        )

        curso = get_object_or_404(
            Curso,
            id=curso_id
        )

        wb = Workbook()

        ws = wb.active

        ws.title = "Aspirantes"

        ws.append([
            "ID",
            "Nombre",
            "Apellido",
            "RUT",
            "Sexo",
            "Edad",
            "Nacionalidad",
            "Estado Civil",
            "Email",
            "Teléfono",
            "Profesión",
            "Nivel Estudios",
            "Situación Laboral",
            "Dirección",
            "Región",
            "Fecha",
            "Curso",
            "Código Curso",
            "Estado",
            "Modificado por",
            "Costo",
            "Ingreso",
            "Total Pagado",
        ])

        for alumno in alumnos:

            ws.append([
                alumno.get("id"),
                alumno.get("nombre"),
                alumno.get("apellido"),
                alumno.get("rut"),
                alumno.get("sexo"),
                alumno.get("edad"),
                alumno.get("nacionalidad"),
                alumno.get("estado_civil"),
                alumno.get("email"),
                alumno.get("telefono"),
                alumno.get("profesion"),
                alumno.get("nivel_estudios"),
                alumno.get("situacion_laboral"),
                alumno.get("direccion"),
                alumno.get("region"),
                alumno.get("fecha"),
                alumno.get("nombre_curso"),
                alumno.get("codigo_curso"),
                alumno.get("estado"),
                alumno.get("modificado_por"),
                alumno.get("costo"),
                alumno.get("ingreso"),
                alumno.get("total_pagos") or 0,
            ])

        archivo = BytesIO()

        wb.save(archivo)

        archivo.seek(0)

        response = HttpResponse(
            archivo.getvalue(),
            content_type=(
                "application/vnd.openxmlformats-"
                "officedocument.spreadsheetml.sheet"
            )
        )

        response[
            "Content-Disposition"
        ] = (
            f'attachment; filename="'
            f'curso_{curso.codigo_curso}.xlsx"'
        )

        return response


    # ============================================
    # EXPORTAR PAGADOS PARA MOODLE
    # ============================================

    @staticmethod
    @require_POST
    def exportar_pagados(request, curso_id):

        alumnos = obtener_aspirantes_por_curso(
            curso_id
        )

        curso = get_object_or_404(
            Curso,
            id=curso_id
        )

        wb = Workbook()

        ws = wb.active

        ws.title = "Moodle"

        ws.append([
            "username",
            "password",
            "firstname",
            "lastname",
            "email",
            "course1",
            "country",
            "lang",
            "timezone",
            "idnumber",
        ])

        for alumno in alumnos:

            estado_id = (
                alumno.get(
                    "id_estado_alumno"
                )
                or 0
            )

            # Misma condición del Flask antiguo
            if estado_id >= 18:

                rut = (
                    alumno.get("rut", "")
                    .replace(".", "")
                    .replace("-", "")
                )

                # El Flask quitaba el DV
                username = rut[:-1]

                password = (
                    username[:4]
                    + "#icL"
                )

                ws.append([
                    username,
                    password,
                    alumno.get("nombre"),
                    alumno.get("apellido"),
                    alumno.get("email"),
                    alumno.get(
                        "codigo_curso"
                    ),
                    "CL",
                    "es_mx",
                    "America/Santiago",
                    alumno.get("id"),
                ])

        archivo = BytesIO()

        wb.save(archivo)

        archivo.seek(0)

        response = HttpResponse(
            archivo.getvalue(),
            content_type=(
                "application/vnd.openxmlformats-"
                "officedocument.spreadsheetml.sheet"
            )
        )

        response[
            "Content-Disposition"
        ] = (
            f'attachment; filename="'
            f'moodle_{curso.codigo_curso}.xlsx"'
        )

        return response


    # ============================================
    # CORREO ACEPTACIÓN
    # ============================================

    @staticmethod
    @require_POST
    @transaction.atomic
    def correo_aceptacion(request, alumno_id):

        curso_id = request.POST.get(
            "curso_id"
        )

        pagina = request.POST.get(
            "pagina",
            "0"
        )

        url_pago = request.POST.get(
            "url_pago"
        )

        origen = request.POST.get(
            "origen",
            "alumnos"
        )
        try:

            alumno, curso, usuario = (
                AlumnoView._datos_correo(
                    request,
                    alumno_id,
                    curso_id
                )
            )

            enviar_email_aceptacion(
                alumno=alumno,
                curso=curso,
                usuario=usuario,
                url_pago=url_pago,
            )

            # Flask agregaba estado 13
            AlumnoView._agregar_estado(
                request,
                alumno,
                13
            )

            messages.success(
                request,
                "Correo de aceptación enviado correctamente."
            )

        except Exception as e:

            messages.error(
                request,
                f"Error enviando correo: {e}"
            )

        return AlumnoView._redirect_alumnos(
            curso_id,
            pagina,
            origen
        )


    # ============================================
    # CORREO PAGO
    # ============================================

    @staticmethod
    @require_POST
    @transaction.atomic
    def correo_pago(request, alumno_id):

        curso_id = request.POST.get(
            "curso_id"
        )

        pagina = request.POST.get(
            "pagina",
            "0"
        )

        medio_pago = request.POST.get(
            "medio_pago"
        )
        origen = request.POST.get(
            "origen",
            "alumnos"
        )
        try:

            alumno, curso, usuario = (
                AlumnoView._datos_correo(
                    request,
                    alumno_id,
                    curso_id
                )
            )

            enviar_email_pago(
                alumno=alumno,
                curso=curso,
                usuario=usuario,
                medio_pago=medio_pago,
            )

            # Flask agregaba estado 19
            AlumnoView._agregar_estado(
                request,
                alumno,
                19
            )

            messages.success(
                request,
                "Correo de pago enviado correctamente."
            )

        except Exception as e:

            messages.error(
                request,
                f"Error enviando correo: {e}"
            )

        return AlumnoView._redirect_alumnos(
            curso_id,
            pagina,
            origen
        )


    # ============================================
    # BIENVENIDA INDIVIDUAL
    # IEMCE / AAMCE / CBC / AAC
    # ============================================

    @staticmethod
    @require_POST
    @transaction.atomic
    def correo_bienvenida_especial(
        request,
        alumno_id
    ):

        curso_id = request.POST.get(
            "curso_id"
        )

        pagina = request.POST.get(
            "pagina",
            "0"
        )

        link_sence = request.POST.get(
            "link_sence"
        )

        tipo = request.POST.get(
            "tipo"
        )
        origen = request.POST.get(
            "origen",
            "alumnos"
        )
        try:

            if tipo not in (
                "IEMCE",
                "AAMCE",
                "CBC",
                "AAC",
            ):

                raise Exception(
                    "Tipo de correo no válido."
                )

            alumno, curso, usuario = (
                AlumnoView._datos_correo(
                    request,
                    alumno_id,
                    curso_id
                )
            )

            enviar_email_bienvenida_especial(
                alumno=alumno,
                curso=curso,
                usuario=usuario,
                link_sence=link_sence,
                tipo=tipo,
            )

            # Flask usaba estado 14
            AlumnoView._agregar_estado(
                request,
                alumno,
                14
            )

            messages.success(
                request,
                f"Correo de bienvenida {tipo} enviado correctamente."
            )

        except Exception as e:

            messages.error(
                request,
                f"Error enviando correo: {e}"
            )

        return AlumnoView._redirect_alumnos(
            curso_id,
            pagina,
            origen
        )


    # ============================================
    # AUXILIARES
    # ============================================

    @staticmethod
    def _datos_correo(
        request,
        alumno_id,
        curso_id
    ):

        alumno = get_object_or_404(
            Alumno,
            id=alumno_id
        )

        curso = get_object_or_404(
            Curso.objects.select_related(
                "id_dias",
                "id_horario"
            ),
            id=curso_id
        )

        usuario_id = request.session.get(
            "id"
        )

        if not usuario_id:

            raise Exception(
                "No existe usuario en sesión."
            )

        usuario = get_object_or_404(
            Usuario,
            id=usuario_id
        )

        return alumno, curso, usuario


    @staticmethod
    def _agregar_estado(
        request,
        alumno,
        estado_id
    ):

        usuario_id = request.session.get(
            "id"
        )

        Alumno_Estado.objects.create(
            id_estado_id=estado_id,
            id_alumno=alumno,
            fecha=timezone.now(),
            id_usuario=usuario_id,
        )


    @staticmethod
    def _redirect_alumnos(
        curso_id,
        pagina=0,
        origen="alumnos"
    ):

        if origen == "busqueda":

            url = reverse(
                "busqueda"
            )

            query = urlencode({
                "pagina": pagina,
            })

        else:

            url = reverse(
                "alumnos"
            )

            query = urlencode({
                "curso": curso_id,
                "pagina": pagina,
            })

        return redirect(
            f"{url}?{query}"
        )

class BusquedaView(ViewCustom):

    @staticmethod
    def busqueda(request):

        estados = obtener_estados_alumno()

        # None significa: TODOS los cursos
        alumnos = obtener_aspirantes_por_curso(None)

        context = {

            "title": "Búsqueda",

            "row_actions":
                "administracion/row_actions/alumnos.html",

            "table_order": "desc",

            "ids": [
                "id",
                "id_curso",
                "id_estado_alumno",
            ],

            "mostrar_estado_alumno": True,

            "atributos": [
                "id",
                "nombre",
                "apellido",
                "rut",
                "email",
                "telefono",
                "nombre_curso",
                "estado",
                "modificado_por",
                "total_pagos",
            ],

            "data": alumnos,

            "estados": estados,

            "total": len(alumnos),

            # Lo usaremos para saber que estamos
            # trabajando desde Búsqueda
            "es_busqueda": True,
        }

        return render(
            request,
            "administracion/busqueda.html",
            context
        )

class CursoView(ViewCustom):

    @staticmethod
    def cursos(request):

        cursos = obtener_cursos_detalle()

        horarios = Horario.objects.all().order_by("-id")
        dias = Dias.objects.all().order_by("-id")

        context = {

            "title": "Cursos",

            "actions_bar":
                "administracion/actions_bar/cursos.html",

            "row_actions":
                "administracion/row_actions/cursos.html",

            "table_order": "desc",

            "mostrar_estado_activo": True,

            "atributos": [
                "id",
                "nombre",
                "codigo_curso",
                "fecha_inicio",
                "fecha_fin",
                "dias",
                "horario",
                "costo",
                "estado",
            ],

            "ids": [
                "id",
                "activo",
            ],

            "data": cursos,

            "horarios": horarios,
            "dias_lista": dias,
        }

        return render(
            request,
            "administracion/cursos.html",
            context
        )


    # ================================================
    # CREATE
    # ================================================

    @staticmethod
    @require_POST
    def agregar_curso(request):

        try:

            nombre = request.POST.get("nombre")
            codigo = request.POST.get("codigo")
            fecha_inicio = request.POST.get("fecha_inicio")
            fecha_fin = request.POST.get("fecha_fin")
            id_dias = request.POST.get("dias")
            id_horario = request.POST.get("horario")
            costo = request.POST.get("costo")
            modalidad = request.POST.get("modalidad")

            if not all([
                nombre,
                codigo,
                fecha_inicio,
                fecha_fin,
                id_dias,
                id_horario,
                costo,
                modalidad
            ]):
                messages.error(
                    request,
                    "Debe completar todos los campos."
                )

                return redirect("cursos")

            Curso.objects.create(

                nombre=nombre,

                codigo_curso=codigo,

                fecha_inicio=fecha_inicio,

                fecha_fin=fecha_fin,

                id_dias_id=id_dias,

                id_horario_id=id_horario,

                costo=costo,

                modalidad=modalidad,

                activo=1
            )

            messages.success(
                request,
                "Curso agregado correctamente."
            )

        except Exception as e:

            messages.error(
                request,
                f"Error al agregar curso: {str(e)}"
            )

        return redirect("cursos")


    # ================================================
    # UPDATE
    # ================================================

    @staticmethod
    @require_POST
    def actualizar_curso(request):

        pagina = request.POST.get("pagina", "0")

        try:

            curso_id = request.POST.get("id_curso")

            curso = get_object_or_404(
                Curso,
                id=curso_id
            )

            curso.nombre = request.POST.get(
                "nombre"
            )

            curso.codigo_curso = request.POST.get(
                "codigo"
            )

            curso.fecha_inicio = request.POST.get(
                "fecha_inicio"
            )

            curso.fecha_fin = request.POST.get(
                "fecha_fin"
            )

            curso.id_dias_id = request.POST.get(
                "dias"
            )

            curso.id_horario_id = request.POST.get(
                "horario"
            )

            curso.costo = request.POST.get(
                "costo"
            )

            curso.modalidad = request.POST.get(
                "modalidad"
            )

            curso.save()

            messages.success(
                request,
                "Curso actualizado correctamente."
            )

        except Exception as e:

            messages.error(
                request,
                f"Error al actualizar curso: {str(e)}"
            )

        return redirect(
            f"{reverse('cursos')}?pagina={pagina}"
        )


    # ================================================
    # DELETE
    # ================================================

    @staticmethod
    @require_POST
    def eliminar_curso(request):

        try:

            curso_id = request.POST.get("id_curso")

            curso = get_object_or_404(
                Curso,
                id=curso_id
            )

            # Evitamos eliminar un curso que ya tenga alumnos
            if Alumno.objects.filter(
                id_curso_id=curso_id
            ).exists():

                messages.error(
                    request,
                    "No se puede eliminar el curso porque tiene alumnos asociados."
                )

                return redirect("cursos")

            # Evitamos eliminar cursos con pagos
            if Pagos.objects.filter(
                id_curso_id=curso_id
            ).exists():

                messages.error(
                    request,
                    "No se puede eliminar el curso porque tiene pagos asociados."
                )

                return redirect("cursos")

            curso.delete()

            messages.success(
                request,
                "Curso eliminado correctamente."
            )

        except Exception as e:

            messages.error(
                request,
                f"Error al eliminar curso: {str(e)}"
            )

        return redirect("cursos")


    @staticmethod
    @require_POST
    def actualizar_estado(request, curso_id):

        pagina = request.POST.get("pagina", "0")

        curso = get_object_or_404(
            Curso,
            id=curso_id
        )

        if curso.activo == 1:

            curso.activo = 0

            mensaje = "Curso desactivado correctamente."

        else:

            curso.activo = 1

            mensaje = "Curso activado correctamente."

        curso.save(
            update_fields=["activo"]
        )

        messages.success(
            request,
            mensaje
        )

        return redirect(
            f"{reverse('cursos')}?pagina={pagina}"
        )


    # ================================================
    # CORREO BIENVENIDA
    # ================================================

    @staticmethod
    @require_POST
    def enviar_correo_bienvenida(request):

        id_curso = request.POST.get(
            "idCurso"
        )

        nombre_curso = request.POST.get(
            "nombreCurso"
        )

        inicio_curso = request.POST.get(
            "inicioCurso"
        )

        horario_curso = request.POST.get(
            "horarioCurso"
        )

        url_zoom = request.POST.get(
            "urlZoom"
        )

        id_reunion_zoom = request.POST.get(
            "idReunionZoom"
        )

        codigo_acceso_zoom = request.POST.get(
            "codigoAccesoZoom"
        )

        nombre_profesor = request.POST.get(
            "nombreProfesor"
        )

        if not all([
            id_curso,
            nombre_curso,
            inicio_curso,
            horario_curso,
            url_zoom,
            id_reunion_zoom,
            codigo_acceso_zoom,
            nombre_profesor,
        ]):

            messages.error(
                request,
                "Debe completar todos los datos del correo de bienvenida."
            )

            return redirect("cursos")

        # ==================================
        # Usuario conectado
        # ==================================

        id_usuario = request.session.get("id")

        if not id_usuario:

            messages.error(
                request,
                "No se encontró el usuario en sesión."
            )

            return redirect("cursos")

        usuario = Usuario.objects.filter(
            id=id_usuario
        ).first()

        if not usuario:

            messages.error(
                request,
                "No se encontró información del usuario."
            )

            return redirect("cursos")

        # ==================================
        # Alumnos pagados
        # Estados 18 o 19
        # ==================================

        alumnos = obtener_alumnos_correo_bienvenida(
            id_curso
        )

        if len(alumnos) == 0:

            messages.warning(
                request,
                "No existen alumnos con estado 18 o 19 para enviar el correo."
            )

            return redirect("cursos")

        enviados = 0
        errores = 0

        estado_bienvenida = Estado_Alumno.objects.filter(
            id=20
        ).first()

        if not estado_bienvenida:

            messages.error(
                request,
                "No existe el estado 20 en Estado_Alumno."
            )

            return redirect("cursos")

        for alumno in alumnos:

            try:

                nombre_alumno = (
                    f"{alumno['nombre']} "
                    f"{alumno['apellido']}"
                )

                # Enviar correo
                enviar_email_bienvenida(

                    nombre=nombre_alumno,

                    correo=alumno["email"],

                    nombre_curso=nombre_curso,

                    url_zoom=url_zoom,

                    id_reunion_zoom=id_reunion_zoom,

                    codigo_acceso_zoom=codigo_acceso_zoom,

                    inicio_curso=inicio_curso,

                    nombre_profesor=nombre_profesor,

                    horario_curso=horario_curso,

                    nombre_usuario=usuario.nombre,

                    correo_usuario=usuario.correo or "",

                    numero_usuario=usuario.numero or "",
                )

                # Solamente cambia de estado
                # si el correo se envió correctamente

                Alumno_Estado.objects.create(

                    id_alumno_id=alumno["id"],

                    id_estado=estado_bienvenida,

                    fecha=timezone.now(),

                    id_usuario=id_usuario
                )

                enviados += 1

            except Exception as e:

                print(
                    f"Error enviando correo "
                    f"a {alumno['email']}: {e}"
                )

                errores += 1

        if enviados > 0:

            messages.success(
                request,
                f"Correos enviados correctamente: {enviados}."
            )

        if errores > 0:

            messages.warning(
                request,
                f"No se pudieron enviar {errores} correos."
            )

        return redirect("cursos") 

class DashboardView(ViewCustom):

    @staticmethod
    def dashboard(request):

        resumen = obtener_dashboard_resumen()

        ultimos_alumnos = (
            obtener_ultimos_alumnos_dashboard(10)
        )

        cursos_activos = (
            obtener_cursos_activos_dashboard()
        )

        alumnos_por_curso = (
            obtener_alumnos_por_curso_activo()
        )

        alumnos_por_horario = (
            obtener_alumnos_por_horario()
        )

        resumen_cursos = obtener_resumen_cursos_activos_dashboard()

        # ============================================
        # HORARIO MAYOR / MENOR INGRESO
        # ============================================

        horario_mayor = None
        horario_menor = None

        if alumnos_por_horario:

            horario_mayor = max(
                alumnos_por_horario,
                key=lambda x: x["cantidad"]
            )

            horario_menor = min(
                alumnos_por_horario,
                key=lambda x: x["cantidad"]
            )


        # ============================================
        # DATOS PARA GRAFICOS
        # ============================================

        cursos_labels = [
            curso["codigo_curso"]
            for curso in alumnos_por_curso
        ]

        cursos_data = [
            curso["cantidad"]
            for curso in alumnos_por_curso
        ]


        horarios_labels = [
            horario["franja"]
            for horario in alumnos_por_horario
        ]

        horarios_data = [
            horario["cantidad"]
            for horario in alumnos_por_horario
        ]


        context = {

            "title": "Dashboard",

            "resumen": resumen,

            "ultimos_alumnos":
                ultimos_alumnos,

            "cursos_activos":
                cursos_activos,

            "horario_mayor":
                horario_mayor,

            "horario_menor":
                horario_menor,

            "cursos_labels":
                json.dumps(cursos_labels),

            "cursos_data":
                json.dumps(cursos_data),

            "horarios_labels":
                json.dumps(horarios_labels),

            "horarios_data":
                json.dumps(horarios_data),

            "resumen_cursos": resumen_cursos,
        }


        return render(
            request,
            "administracion/dashboard.html",
            context
        )
