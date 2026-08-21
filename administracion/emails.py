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
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[correo],
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

    context = _contexto_base(
        alumno,
        curso,
        usuario
    )

    context["link_sence"] = link_sence
    context["tipo"] = tipo

    # Configuración según correo original Flask
    if tipo == "IEMCE":

        context["horas"] = 40
        context["valor_total"] = None

        context["descripcion"] = (
            "Los preparamos para desempeñarse en establecimientos "
            "públicos o privados. Quedarás capacitado para aplicar "
            "estrategias de convivencia escolar, atención de primeros "
            "auxilios, mediación de conflictos y todo lo necesario "
            "para desempeñarse como Inspector Educacional."
        )

        context["texto_practica"] = (
            "IC Capacitación Laboral te apoya en la gestión de tu "
            "proceso de Práctica Laboral, enviando un certificado de "
            "solicitud formal al establecimiento al que decidas "
            "postular para trabajar como Inspector Educacional."
        )

        context["cuotas"] = [
            "$25.000.- para guardar cupo",
            "$25.000.- al comienzo de clases",
            "$35.000.- al término de clases",
        ]

        context["cuotas_dos"] = []


    elif tipo == "AAMCE":

        context["horas"] = 40
        context["valor_total"] = "319.990"

        context["descripcion"] = (
            "Los preparamos para desempeñarse en establecimientos "
            "públicos o privados. Quedarás capacitado para aplicar "
            "estrategias de convivencia escolar, Necesidades "
            "Educativas Especiales, resolución de conflictos y todo "
            "lo necesario para desempeñarte como Asistente de Aula."
        )

        context["texto_practica"] = (
            "IC Capacitación Laboral te apoya en la gestión de tu "
            "Práctica Laboral (no obligatoria). Se enviará una carta "
            "de solicitud formal al establecimiento al que decidas "
            "postular para trabajar como Asistente de Aula."
        )

        context["cuotas"] = [
            "$20.000.- para guardar cupo",
            "$20.000.- al comienzo de clases",
            "$39.990.- al término de clases",
        ]

        context["cuotas_dos"] = [
            "$40.000.- inicio del curso",
            "$39.990.- término del curso",
        ]


    elif tipo == "CBC":

        context["horas"] = 36
        context["valor_total"] = "340.000"

        context["descripcion"] = (
            "Está dirigido a personas que deseen adquirir "
            "conocimientos y herramientas técnicas para la adecuada "
            "manipulación y operación de una caja bancaria o "
            "comercial. Podrás desarrollar el perfil de competencias "
            "requerido para operar una caja dentro de una institución "
            "bancaria, financiera o empresa del rubro retail."
        )

        context["texto_practica"] = (
            "IC Capacitación Laboral te apoya en la gestión de tu "
            "Práctica Laboral (no obligatoria), enviando una carta de "
            "solicitud formal al establecimiento donde decidas "
            "postular."
        )

        context["cuotas"] = [
            "$25.000.- para guardar cupo",
            "$25.000.- al comienzo de clases",
            "$35.000.- al término de clases",
        ]

        context["cuotas_dos"] = []


    elif tipo == "AAC":

        context["horas"] = 36
        context["valor_total"] = "340.000"

        context["descripcion"] = (
            "El curso está orientado a comprender el concepto de "
            "empresa y sus tipos, además de conocer quiénes se "
            "desempeñan en ellas para realizar labores de "
            "administración, gestión, control, facturación y cobranza "
            "respetando las disposiciones legales vigentes."
        )

        context["texto_practica"] = (
            "IC Capacitación Laboral te apoya en la gestión de tu "
            "Práctica Laboral (no obligatoria), enviando una carta de "
            "solicitud formal al establecimiento donde decidas "
            "postular."
        )

        context["cuotas"] = [
            "$25.000.- para guardar cupo",
            "$25.000.- al comienzo de clases",
            "$35.000.- al término de clases",
        ]

        context["cuotas_dos"] = []

    else:

        raise ValueError(
            f"Tipo de correo de bienvenida no válido: {tipo}"
        )


    _enviar_template(
        (
            "¡Felicitaciones! Fuiste beneficiado con nuestra "
            "beca ICL con un 75% de descuento"
        ),
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