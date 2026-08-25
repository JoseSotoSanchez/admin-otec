from django.conf import settings
from django.core.mail import (
    EmailMultiAlternatives,
    get_connection,
)
from django.template.loader import render_to_string
from email.utils import formataddr

def enviar_email_bienvenida(
    nombre,
    correo,
    nombre_curso,
    url_zoom,
    id_reunion_zoom,
    codigo_acceso_zoom,
    inicio_curso,
    nombre_profesor,
    horario_curso,
    nombre_usuario,
    correo_usuario,
    numero_usuario
 ):
    subject = f"Bienvenido(a) al curso {nombre_curso}"

    context = {
        "nombre": nombre,
        "nombre_curso": nombre_curso,
        "url_zoom": url_zoom,
        "id_reunion_zoom": id_reunion_zoom,
        "codigo_acceso_zoom": codigo_acceso_zoom,
        "inicio_curso": inicio_curso,
        "nombre_profesor": nombre_profesor,
        "horario_curso": horario_curso,
        "nombre_usuario": nombre_usuario,
        "correo_usuario": correo_usuario,
        "numero_usuario": numero_usuario,
    }

    html_content = render_to_string(
        "administracion/emails/bienvenida.html",
        context
    )

    email = EmailMultiAlternatives(
        subject=subject,
        body=f"Bienvenido al curso {nombre_curso}",
        from_email=formataddr(
            (
                "IC Capacitación Laboral",
                settings.EMAIL_POSTULACIONES_USER
            )
        ),
        to=[correo],
        connection=_conexion_postulaciones(),
    )

    email.attach_alternative(html_content, "text/html")

    email.send(fail_silently=False)

def _enviar_template(
    asunto,
    destinatario,
    template,
    context,
    cuenta="postulaciones"
):

    html = render_to_string(
        template,
        context
    )


    if cuenta == "pagos":

        conexion = _conexion_pagos()

        remitente = (
            settings.EMAIL_PAGOS_USER
        )


    elif cuenta == "administracion":

        conexion = (
            _conexion_administracion()
        )

        remitente = (
            settings.EMAIL_ADMINISTRACION_USER
        )


    else:

        conexion = (
            _conexion_postulaciones()
        )

        remitente = (
            settings.EMAIL_POSTULACIONES_USER
        )


        email = EmailMultiAlternatives(
        subject=asunto,
        body=asunto,
        from_email=formataddr(
            (
                "IC Capacitación Laboral",
                remitente
            )
        ),
        to=[destinatario],
        connection=conexion,
    )

    email.attach_alternative(
        html,
        "text/html"
    )

    email.send(
        fail_silently=False
    )


def _contexto_base(
    alumno,
    curso,
    usuario
):

    nombre_alumno = (
        f"{alumno.nombre} {alumno.apellido}"
    )

    return {

        "alumno": alumno,

        "curso": curso,

        "usuario": usuario,

        "nombre_alumno": nombre_alumno,

        "fecha_inicio":
            curso.fecha_inicio.strftime(
                "%d-%m-%Y"
            )
            if curso.fecha_inicio
            else "",

        "fecha_fin":
            curso.fecha_fin.strftime(
                "%d-%m-%Y"
            )
            if curso.fecha_fin
            else "",

        "dias":
            curso.id_dias.rango,

        "horario":
            curso.id_horario.rango,

        "modalidad":
            curso.modalidad or "",

        "valor_curso":
            f"{curso.costo:,}"
            .replace(",", "."),

    }


def enviar_email_aceptacion(
    alumno,
    curso,
    usuario,
    url_pago
):

    context = _contexto_base(
        alumno,
        curso,
        usuario
    )

    context[
        "url_pago"
    ] = url_pago

    context[
        "porcentaje"
    ] = (
        50
        if "Corredor" in curso.nombre
        else 75
    )

    _enviar_template(
        "Postulación aceptada - IC Capacitación Laboral",
        alumno.email,
        "administracion/emails/aceptacion.html",
        context,
        cuenta="postulaciones"
    )


def enviar_email_pago(
    alumno,
    curso,
    usuario,
    medio_pago
):

    context = _contexto_base(
        alumno,
        curso,
        usuario
    )

    context[
        "medio_pago"
    ] = medio_pago

    _enviar_template(
        "Información de pago - IC Capacitación Laboral",
        alumno.email,
        "administracion/emails/pago.html",
        context,
        cuenta="pagos"
    )


def enviar_email_bienvenida_especial(
    alumno,
    curso,
    usuario,
    link_sence,
    tipo
):

    tipo = (tipo or "").upper()


    # ============================================
    # CONFIGURACION EXACTA SEGUN CORREO ANTIGUO
    # ============================================

    configuracion = {

        # ========================================
        # IEMCE
        # ========================================

        "IEMCE": {

            "horas": 54,

            "descripcion_1": (
                f"El Curso de {curso.nombre} le otorgará todas las "
                "herramientas y conocimientos necesarios para llevar "
                "a cabo su inserción laboral con una alta eficacia. "
                "Los preparamos para desempeñarse en establecimientos "
                "públicos o privados, quedarás capacitado para aplicar "
                "estrategias de convivencia escolar, atención de "
                "primeros auxilios, mediación de conflictos y todo lo "
                "necesario que debes saber para ser un Inspector "
                "Educación (Patio). Te dejamos Link para que puedas "
                "verificar que somos Acreditados por SENCE y la norma "
                "NCH 2728/ 2015 del sistema nacional de acreditación "
                "INN-Chile."
            ),

            "descripcion_2": "",

            "descripcion_3": "",

            "texto_sence_1":
                "Le dejamos link",

            "texto_sence_2":
                "Para que verifiquen que somos acreditados por Sence.",

            "texto_sence_3":
                "Link de Organismos Técnicos de Capacitación "
                "Acreditados por Sence:",

            "mostrar_rut_sence": True,

            "texto_practica": (
                "Te apoya en la gestión de tú proceso de Práctica "
                "Laboral, enviando un certificado de solicitud formal "
                "al establecimiento al que tú decidas postular para "
                "trabajar como Inspector Educacional. Para esto solo "
                "necesitamos que nos consigas el contacto de la persona "
                "encargada de personal. (Una vez aceptada la solicitud "
                "procedemos a enviar la documentación para tu evaluación) "
                "todo esto sin costo adicional."
            ),

            "mostrar_puede_trabajar": False,

            "mostrar_valor_total": False,

            "valor_total": "",

            "mostrar_dos_cuotas": False,

            "cuotas_dos": [],
        },


        # ========================================
        # AAMCE
        # ========================================

        "AAMCE": {

            "horas": 54,

            "descripcion_1": (
                f"El Curso de {curso.nombre} le otorgará todas las "
                "herramientas y conocimientos necesarios para llevar "
                "a cabo su inserción laboral con una alta eficacia. "
                "Los preparamos para desempeñarse en establecimientos "
                "públicos o privados, quedarás capacitado para aplicar "
                "estrategias de convivencia escolar, Necesidades "
                "Especiales Educativas, Resolución de conflictos y todo "
                "lo necesario que debes saber para ser un Asistente "
                "de Aula."
            ),

            "descripcion_2": "",

            "descripcion_3": "",

            "texto_sence_1": (
                "Te dejamos Link para que puedas verificar que somos "
                "Acreditados por SENCE y la norma NCH 2728/ 2015 del "
                "sistema nacional de acreditación INN- Chile. Para que "
                "verifiquen que somos acreditados por Sence."
            ),

            "texto_sence_2": "",

            "texto_sence_3":
                "Link de Organismos Técnicos de Capacitación "
                "Acreditados por Sence:",

            "mostrar_rut_sence": False,

            "texto_practica": (
                "Te apoya en la gestión de tú proceso de Práctica "
                "Laboral (No Obligatorio), Se enviará una carta de "
                "solicitud formal al establecimiento al que tú decidas "
                "postular para trabajar como Asistente Aula. Para esto "
                "solo necesitamos nos consigas el contacto de la persona "
                "encargada de personal para hacer la gestión de "
                "Postulación Acreditación Sence. "
                "(Todo esto sin costó adicional)"
            ),

            "mostrar_puede_trabajar": True,

            "mostrar_valor_total": True,

            "valor_total": "319.990",

            "mostrar_dos_cuotas": True,

            "cuotas_dos": [
                "$40.000.- Inicio del curso",
                "$39.990.- Término del curso",
            ],
        },


        # ========================================
        # CBC
        # ========================================

        "CBC": {

            "horas": 50,

            "descripcion_1": (
                f"El Curso de {curso.nombre} le otorgará todas las "
                "herramientas y conocimientos necesarios para llevar "
                "a cabo su inserción laboral con una alta eficacia."
            ),

            "descripcion_2": (
                "Está dirigido a personas que deseen adquirir "
                "conocimientos y herramientas técnicas, para la adecuada "
                "manipulación y operación de una caja bancaria o "
                "comercial. Podrás desarrollar el perfil de competencias "
                "que se requiere para operar una caja, dentro de una "
                "institución bancaria, financiera o empresa del rubro "
                "retail o también conocido como venta al detalle o "
                "comercio minorista de productos o servicios."
            ),

            "descripcion_3": (
                "Le entregaremos los conocimientos necesarios para que "
                "puedas desempeñarte con un perfil laboral competente "
                "y cubrir el puesto de trabajo esperado."
            ),

            "texto_sence_1": (
                "Te dejamos Link para que puedas verificar que somos "
                "Acreditados por SENCE y la norma NCH 2728/ 2015 del "
                "sistema nacional de acreditación INN- Chile."
            ),

            "texto_sence_2":
                "Para que verifiquen que somos acreditados por Sence.",

            "texto_sence_3": "",

            "mostrar_rut_sence": False,

            "texto_practica": (
                "Te apoya en la gestión de tú proceso de Práctica "
                f"Laboral (No Obligatorio), Se enviará una carta de "
                f"solicitud formal al establecimiento al que tú decidas "
                f"postular para trabajar como {curso.nombre}. Para esto "
                "solo necesitamos nos consigas el contacto de la persona "
                "encargada de personal para hacer la gestión de "
                "Postulación Acreditación Sence. "
                "(Todo esto sin costó adicional)"
            ),

            "mostrar_puede_trabajar": True,

            "mostrar_valor_total": True,

            "valor_total": "340.000",

            "mostrar_dos_cuotas": False,

            "cuotas_dos": [],
        },


        # ========================================
        # AAC
        # ========================================

        "AAC": {

            "horas": 50,

            "descripcion_1": (
                f"El Curso de {curso.nombre} le otorgará todas las "
                "herramientas y conocimientos necesarios para llevar "
                "a cabo su inserción laboral con una alta eficacia."
            ),

            "descripcion_2": (
                "El curso está orientado a que la persona pueda "
                "comprender el concepto de empresa y sus tipos, además "
                "de saber quiénes se desempeñan en ellas para así poder "
                "realizar la administración, gestión, control y "
                "contabilidad de facturación y cobranza de las mismas "
                "respetando las disposiciones legales vigentes. De este "
                "modo, ser una ayuda y contribuir en las organizaciones."
            ),

            "descripcion_3": (
                "Le entregaremos los conocimientos necesarios para que "
                "puedas desempeñarte con un perfil laboral competente "
                "y cubrir el puesto de trabajo esperado."
            ),

            "texto_sence_1": (
                "Te dejamos Link para que puedas verificar que somos "
                "Acreditados por SENCE y la norma NCH 2728/ 2015 del "
                "sistema nacional de acreditación INN- Chile."
            ),

            "texto_sence_2":
                "Para que verifiquen que somos acreditados por Sence.",

            "texto_sence_3": "",

            "mostrar_rut_sence": False,

            "texto_practica": (
                "Te apoya en la gestión de tú proceso de Práctica "
                f"Laboral (No Obligatorio), Se enviará una carta de "
                f"solicitud formal al establecimiento al que tú decidas "
                f"postular para trabajar como {curso.nombre}. Para esto "
                "solo necesitamos nos consigas el contacto de la persona "
                "encargada de personal para hacer la gestión de "
                "Postulación Acreditación Sence. "
                "(Todo esto sin costó adicional)"
            ),

            "mostrar_puede_trabajar": True,

            "mostrar_valor_total": True,

            "valor_total": "340.000",

            "mostrar_dos_cuotas": False,

            "cuotas_dos": [],
        },
    }


    if tipo not in configuracion:

        raise ValueError(
            f"Tipo de correo de bienvenida no válido: {tipo}"
        )


    datos = configuracion[tipo]


    # ============================================
    # FORMATEO DATOS
    # ============================================

    nombre_alumno = (
        f"{alumno.nombre} {alumno.apellido}"
    ).strip().title()


    valor_curso = (
        f"{curso.costo:,}".replace(",", ".")
        if curso.costo
        else "0"
    )


    context = {

        "tipo": tipo,

        "nombre": nombre_alumno,

        "nombreCurso": curso.nombre,

        "inicioCurso": (
            curso.fecha_inicio.strftime("%d-%m-%Y")
            if curso.fecha_inicio
            else ""
        ),

        "finCurso": (
            curso.fecha_fin.strftime("%d-%m-%Y")
            if curso.fecha_fin
            else ""
        ),

        "diasCurso": (
            curso.id_dias.rango
            if curso.id_dias
            else ""
        ),

        "horarioCurso": (
            curso.id_horario.rango
            if curso.id_horario
            else ""
        ),

        "modalidad": (
            curso.modalidad or ""
        ),

        "linkSense": link_sence,

        "nombreUsuario": (
            usuario.nombre or ""
        ),

        "correoUsuario": (
            usuario.correo or ""
        ),

        "numeroUsuario": (
            usuario.numero or ""
        ),

        "valorCurso": valor_curso,


        # ESPECIFICOS
        "horas":
            datos["horas"],

        "descripcion_1":
            datos["descripcion_1"],

        "descripcion_2":
            datos["descripcion_2"],

        "descripcion_3":
            datos["descripcion_3"],

        "texto_sence_1":
            datos["texto_sence_1"],

        "texto_sence_2":
            datos["texto_sence_2"],

        "texto_sence_3":
            datos["texto_sence_3"],

        "mostrar_rut_sence":
            datos["mostrar_rut_sence"],

        "texto_practica":
            datos["texto_practica"],

        "mostrar_puede_trabajar":
            datos["mostrar_puede_trabajar"],

        "mostrar_valor_total":
            datos["mostrar_valor_total"],

        "valor_total":
            datos["valor_total"],

        "mostrar_dos_cuotas":
            datos["mostrar_dos_cuotas"],

        "cuotas_dos":
            datos["cuotas_dos"],
    }


    asunto = (
        "¡Felicitaciones! Fuiste beneficiado "
        "con nuestra beca ICL con un 75% de descuento"
    )


    return _enviar_template(
        asunto,
        alumno.email,
        "administracion/emails/bienvenida_especial.html",
        context,
        cuenta="postulaciones"
    )

def _conexion_postulaciones():

    return get_connection(
        backend="django.core.mail.backends.smtp.EmailBackend",
        host=settings.EMAIL_HOST,
        port=settings.EMAIL_PORT,
        username=settings.EMAIL_POSTULACIONES_USER,
        password=settings.EMAIL_POSTULACIONES_PASSWORD,
        use_tls=settings.EMAIL_USE_TLS,
    )


def _conexion_pagos():

    return get_connection(
        backend="django.core.mail.backends.smtp.EmailBackend",
        host=settings.EMAIL_HOST,
        port=settings.EMAIL_PORT,
        username=settings.EMAIL_PAGOS_USER,
        password=settings.EMAIL_PAGOS_PASSWORD,
        use_tls=settings.EMAIL_USE_TLS,
    )


def _conexion_administracion():

    return get_connection(
        backend="django.core.mail.backends.smtp.EmailBackend",
        host=settings.EMAIL_HOST,
        port=settings.EMAIL_PORT,
        username=settings.EMAIL_ADMINISTRACION_USER,
        password=settings.EMAIL_ADMINISTRACION_PASSWORD,
        use_tls=settings.EMAIL_USE_TLS,
    )