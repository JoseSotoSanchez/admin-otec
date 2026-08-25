from django.conf import settings
from django.core.mail import (
    EmailMultiAlternatives,
    get_connection,
)
from django.template.loader import render_to_string

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
        from_email=settings.EMAIL_POSTULACIONES_USER,
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
        from_email=remitente,
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
    # CONFIGURACIÓN SEGÚN CURSO
    # ============================================

    configuracion = {

        "IEMCE": {

            "horas": 54,

            "descripcion": (
                "Los preparamos para desempeñarse en establecimientos "
                "públicos o privados. Quedarás capacitado para aplicar "
                "estrategias de convivencia escolar, atención de primeros "
                "auxilios, mediación de conflictos y todo lo necesario "
                "para desempeñarse como Inspector Educacional."
            ),

            "texto_practica": (
                "IC Capacitación Laboral te apoya en la gestión de tu "
                "proceso de Práctica Laboral, enviando un certificado de "
                "solicitud formal al establecimiento al que decidas "
                "postular para trabajar como Inspector Educacional."
            ),

            "valor_total": None,

            "mostrar_valor_total": False,

            "mostrar_dos_cuotas": False,

            "cuotas_dos": [],
        },


        "AAMCE": {

            "horas": 54,

            "descripcion": (
                "Los preparamos para desempeñarse en establecimientos "
                "públicos o privados. Quedarás capacitado para aplicar "
                "estrategias de convivencia escolar, Necesidades "
                "Educativas Especiales, resolución de conflictos y todo "
                "lo necesario para desempeñarte como Asistente de Aula."
            ),

            "texto_practica": (
                "IC Capacitación Laboral te apoya en la gestión de tu "
                "Práctica Laboral, la cual no es obligatoria. Se enviará "
                "una carta de solicitud formal al establecimiento al que "
                "decidas postular para trabajar como Asistente de Aula."
            ),

            "valor_total": "319.990",

            "mostrar_valor_total": True,

            "mostrar_dos_cuotas": True,

            "cuotas_dos": [
                "$40.000.- Inicio del curso",
                "$39.990.- Término del curso",
            ],
        },


        "CBC": {

            "horas": 50,

            "descripcion": (
                "Está dirigido a personas que deseen adquirir "
                "conocimientos y herramientas técnicas para la adecuada "
                "manipulación y operación de una caja bancaria o "
                "comercial. Podrás desarrollar el perfil de competencias "
                "requerido para operar una caja dentro de una institución "
                "bancaria, financiera o empresa del rubro retail."
            ),

            "texto_practica": (
                "IC Capacitación Laboral te apoya en la gestión de tu "
                "Práctica Laboral, la cual no es obligatoria, enviando "
                "una carta de solicitud formal al establecimiento donde "
                "decidas postular."
            ),

            "valor_total": "340.000",

            "mostrar_valor_total": True,

            "mostrar_dos_cuotas": False,

            "cuotas_dos": [],
        },


        "AAC": {

            "horas": 50,

            "descripcion": (
                "El curso está orientado a comprender el concepto de "
                "empresa y sus tipos, además de conocer quiénes se "
                "desempeñan en ellas para realizar labores de "
                "administración, gestión, control, facturación y cobranza "
                "respetando las disposiciones legales vigentes."
            ),

            "texto_practica": (
                "IC Capacitación Laboral te apoya en la gestión de tu "
                "Práctica Laboral, la cual no es obligatoria, enviando "
                "una carta de solicitud formal al establecimiento donde "
                "decidas postular."
            ),

            "valor_total": "340.000",

            "mostrar_valor_total": True,

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
    # DATOS GENERALES
    # ============================================

    nombre_alumno = (
        f"{alumno.nombre} {alumno.apellido}"
    ).strip().title()


    valor_curso = (
        f"{curso.costo:,}".replace(",", ".")
        if curso.costo
        else "0"
    )


    inicio_curso = (
        curso.fecha_inicio.strftime("%d-%m-%Y")
        if curso.fecha_inicio
        else ""
    )


    fin_curso = (
        curso.fecha_fin.strftime("%d-%m-%Y")
        if curso.fecha_fin
        else ""
    )


    # ============================================
    # CONTEXTO TEMPLATE
    # ============================================

    context = {

        "tipo":
            tipo,

        "nombre":
            nombre_alumno,

        "nombreCurso":
            curso.nombre,

        "inicioCurso":
            inicio_curso,

        "finCurso":
            fin_curso,

        "diasCurso":
            curso.id_dias.rango
            if curso.id_dias
            else "",

        "horarioCurso":
            curso.id_horario.rango
            if curso.id_horario
            else "",

        "modalidad":
            curso.modalidad or "",

        "linkSense":
            link_sence,

        "nombreUsuario":
            usuario.nombre or "",

        "correoUsuario":
            usuario.correo or "",

        "numeroUsuario":
            usuario.numero or "",

        "valorCurso":
            valor_curso,

        # ESPECÍFICOS
        "horas":
            datos["horas"],

        "descripcion":
            datos["descripcion"],

        "texto_practica":
            datos["texto_practica"],

        "valor_total":
            datos["valor_total"],

        "mostrar_valor_total":
            datos["mostrar_valor_total"],

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