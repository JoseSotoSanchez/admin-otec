from django.conf import settings
from django.core.mail import EmailMultiAlternatives
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