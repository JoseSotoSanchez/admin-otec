from django.urls import path
from .views import AlumnoView, CursoView, DashboardView

urlpatterns = [

    # DASHBOARD
    path(
        "dashboard",
        DashboardView.dashboard,
        name="dashboard"
    ),

    # ALUMNOS
    path(
        "",
        AlumnoView.alumnos,
        name="alumnos"
    ),

    path(
        "alumnos",
        AlumnoView.alumnos,
        name="alumnos"
    ),

    # CURSOS
    path(
        "cursos",
        CursoView.cursos,
        name="cursos"
    ),

    path(
        "cursos/agregar",
        CursoView.agregar_curso,
        name="curso_agregar"
    ),

    path(
        "cursos/actualizar",
        CursoView.actualizar_curso,
        name="curso_actualizar"
    ),

    path(
        "cursos/eliminar",
        CursoView.eliminar_curso,
        name="curso_eliminar"
    ),

    path(
        "cursos/<int:curso_id>/estado",
        CursoView.actualizar_estado,
        name="curso_estado"
    ),

    path(
        "cursos/enviar-bienvenida",
        CursoView.enviar_correo_bienvenida,
        name="curso_enviar_bienvenida"
    ),
]