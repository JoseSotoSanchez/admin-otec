from django.urls import path
from .views import (
    AlumnoView,
    CursoView,
    DashboardView,
    AuthView,
    BusquedaView,
    MoverAspirantesView,
    UsuarioView,
)

urlpatterns = [

      # =============================================
    # LOGIN
    # =============================================

    path(
        "login",
        AuthView.login,
        name="login"
    ),

    path(
        "logout",
        AuthView.logout,
        name="logout"
    ),


    # =============================================
    # DASHBOARD
    # =============================================
    path(
        "dashboard",
        DashboardView.dashboard,
        name="dashboard"
    ),

    # =============================================
    # ALUMNOS
    # =============================================
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

    # =============================================
    # BUSQUEDA
    # =============================================

    path(
        "busqueda",
        BusquedaView.busqueda,
        name="busqueda"
    ),
    # =============================================
    # MOVER ASPIRANTES
    # =============================================

    path(
        "mover-aspirantes",
        MoverAspirantesView.mover,
        name="mover_aspirantes"
    ),

    path(
        "mover-aspirantes/uno",
        MoverAspirantesView.mover_uno,
        name="mover_aspirante_uno"
    ),

    path(
        "mover-aspirantes/todos",
        MoverAspirantesView.mover_todos,
        name="mover_aspirantes_todos"
    ),
    # =============================================
    # CURSOS
    # =============================================
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

    # =============================================
    # ASPIRANTES
    # =============================================

    path(
        "alumnos/<int:alumno_id>/actualizar",
        AlumnoView.actualizar_alumno,
        name="alumno_actualizar"
    ),

    path(
        "alumnos/<int:alumno_id>/pago",
        AlumnoView.guardar_pago,
        name="alumno_pago"
    ),

    path(
        "alumnos/<int:alumno_id>/curso/<int:curso_id>/pagos",
        AlumnoView.pagos,
        name="alumno_pagos"
    ),

    path(
        "alumnos/curso/<int:curso_id>/exportar",
        AlumnoView.exportar_alumnos,
        name="alumnos_exportar"
    ),

    path(
        "alumnos/curso/<int:curso_id>/exportar-pagados",
        AlumnoView.exportar_pagados,
        name="alumnos_exportar_pagados"
    ),

    path(
        "alumnos/<int:alumno_id>/correo-aceptacion",
        AlumnoView.correo_aceptacion,
        name="alumno_correo_aceptacion"
    ),

    path(
        "alumnos/<int:alumno_id>/correo-pago",
        AlumnoView.correo_pago,
        name="alumno_correo_pago"
    ),

    path(
        "alumnos/<int:alumno_id>/correo-bienvenida",
        AlumnoView.correo_bienvenida_especial,
        name="alumno_correo_bienvenida"
    ),

    # =============================================
    # USUARIOS
    # =============================================

    path(
        "usuarios",
        UsuarioView.usuarios,
        name="usuarios"
    ),

    path(
        "usuarios/agregar",
        UsuarioView.agregar_usuario,
        name="usuario_agregar"
    ),

    path(
        "usuarios/actualizar",
        UsuarioView.actualizar_usuario,
        name="usuario_actualizar"
    ),

    path(
        "usuarios/<int:usuario_id>/estado",
        UsuarioView.actualizar_estado,
        name="usuario_estado"
    ),
]