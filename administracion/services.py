from django.db import connection


def obtener_aspirantes_por_curso(curso_id):

    with connection.cursor() as cursor:

        query = """
            SELECT
                a.id AS id,
                a.nombre,
                a.apellido,
                a.rut,
                a.sexo,
                a.edad,
                a.nacionalidad,
                a.estado_civil,
                a.email,
                a.telefono,
                a.profesion,
                a.nivel_estudios,
                a.situacion_laboral,
                a.direccion,
                a.region,
                a.fecha,

                c.nombre AS nombre_curso,
                c.codigo_curso,
                c.id AS id_curso,

                ea.estado,
                ea.id AS id_estado_alumno,

                u.nick AS modificado_por,

                c.costo,
                a.ingreso,

                (
                    SELECT SUM(p.monto)
                    FROM Pagos p
                    WHERE p.id_alumno = a.id
                    AND p.id_curso = a.id_curso
                ) AS total_pagos

            FROM Alumno a

            INNER JOIN Curso c
                ON c.id = a.id_curso

            INNER JOIN Alumno_Estado ae
                ON ae.id = (
                    SELECT ae2.id
                    FROM Alumno_Estado ae2
                    WHERE ae2.id_alumno = a.id
                    ORDER BY
                        ae2.fecha DESC,
                        ae2.id DESC
                    LIMIT 1
                )

            INNER JOIN Estado_Alumno ea
                ON ea.id = ae.id_estado

            INNER JOIN Usuario u
                ON u.id = ae.id_usuario

            WHERE 1 = 1
        """

        parametros = []

        if curso_id is not None:

            query += """
                AND c.id = %s
            """

            parametros.append(
                curso_id
            )

        query += """
            ORDER BY a.id DESC
        """

        cursor.execute(
            query,
            parametros
        )

        columnas = [
            col[0]
            for col in cursor.description
        ]

        return [
            dict(zip(columnas, fila))
            for fila in cursor.fetchall()
        ]

def obtener_cursos():

    with connection.cursor() as cursor:

        cursor.execute("""
            SELECT
                id,
                nombre,
                codigo_curso
            FROM Curso
            ORDER BY id DESC
        """)

        columnas = [col[0] for col in cursor.description]

        return [
            dict(zip(columnas, fila))
            for fila in cursor.fetchall()
        ]
def obtener_cursos_detalle():

    with connection.cursor() as cursor:

        cursor.execute("""
            SELECT
                c.id,
                c.nombre,
                c.codigo_curso,
                c.fecha_inicio,
                c.fecha_fin,
                c.id_dias,
                c.id_horario,
                c.costo,
                c.modalidad,
                c.activo,
                d.rango AS dias,
                h.rango AS horario

            FROM Curso c

            INNER JOIN Dias d
                ON d.id = c.id_dias

            INNER JOIN Horario h
                ON h.id = c.id_horario

            ORDER BY c.id DESC
        """)

        columnas = [
            col[0]
            for col in cursor.description
        ]

        cursos = [
            dict(zip(columnas, fila))
            for fila in cursor.fetchall()
        ]


    for curso in cursos:

        # ====================================
        # FECHA INICIO
        # ====================================

        if curso["fecha_inicio"]:

            curso["fecha_inicio_input"] = (
                curso["fecha_inicio"].strftime(
                    "%Y-%m-%d"
                )
            )

            curso["fecha_inicio_correo"] = (
                curso["fecha_inicio"].strftime(
                    "%d-%m-%Y"
                )
            )

            curso["fecha_inicio"] = (
                curso["fecha_inicio"].strftime(
                    "%d-%m-%Y"
                )
            )

        else:

            curso["fecha_inicio_input"] = ""
            curso["fecha_inicio_correo"] = ""
            curso["fecha_inicio"] = ""


        # ====================================
        # FECHA FIN
        # ====================================

        if curso["fecha_fin"]:

            curso["fecha_fin_input"] = (
                curso["fecha_fin"].strftime(
                    "%Y-%m-%d"
                )
            )

            curso["fecha_fin"] = (
                curso["fecha_fin"].strftime(
                    "%d-%m-%Y"
                )
            )

        else:

            curso["fecha_fin_input"] = ""
            curso["fecha_fin"] = ""


        curso["estado"] = (
            "Activo"
            if curso["activo"] == 1
            else "Inactivo"
        )


    return cursos


def obtener_alumnos_correo_bienvenida(curso_id):
    """
    Obtiene alumnos cuyo ÚLTIMO estado sea 18 o 19.
    """

    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT DISTINCT
                a.id,
                a.nombre,
                a.apellido,
                a.email
            FROM Alumno_Estado ae
            INNER JOIN Alumno a
                ON a.id = ae.id_alumno
            INNER JOIN Curso c
                ON c.id = a.id_curso

            WHERE ae.id_estado = (
                SELECT de.id_estado
                FROM Alumno_Estado de
                WHERE de.id_alumno = ae.id_alumno
                ORDER BY de.fecha DESC, de.id DESC
                LIMIT 1
            )

            AND c.id = %s
            AND ae.id_estado IN (18, 19)

            ORDER BY a.id DESC
        """, [curso_id])

        columnas = [col[0] for col in cursor.description]

        return [
            dict(zip(columnas, fila))
            for fila in cursor.fetchall()
        ]

def obtener_estados_alumno():
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT id, estado
            FROM Estado_Alumno
            ORDER BY id
        """)

        return [
            {
                "id": fila[0],
                "estado": fila[1],
            }
            for fila in cursor.fetchall()
        ]


def obtener_pagos_alumno(alumno_id, curso_id):
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT
                id,
                monto,
                medio_pago,
                fecha
            FROM Pagos
            WHERE id_alumno = %s
              AND id_curso = %s
            ORDER BY id DESC
        """, [alumno_id, curso_id])

        columnas = [
            col[0]
            for col in cursor.description
        ]

        return [
            dict(zip(columnas, fila))
            for fila in cursor.fetchall()
        ]