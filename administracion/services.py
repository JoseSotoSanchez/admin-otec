from django.db import connection


def obtener_aspirantes_por_curso(curso_id):

    with connection.cursor() as cursor:

        cursor.execute("""
            SELECT DISTINCT
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

                ea.estado,
                u.nick AS modificado_por,
                ea.id AS id_estado_alumno,

                c.costo,
                a.ingreso,

                (
                    SELECT SUM(p.monto)
                    FROM Pagos p
                    WHERE p.id_alumno = a.id
                    AND p.id_curso = a.id_curso
                ) AS total_pagos

            FROM Alumno_Estado ae

            INNER JOIN Alumno a
                ON a.id = ae.id_alumno

            INNER JOIN Curso c
                ON c.id = a.id_curso

            INNER JOIN Estado_Alumno ea
                ON ea.id = ae.id_estado

            INNER JOIN Usuario u
                ON u.id = ae.id_usuario

            WHERE ae.id_estado = (

                SELECT de.id_estado
                FROM Alumno_Estado de
                WHERE de.id_alumno = ae.id_alumno
                ORDER BY de.fecha DESC
                LIMIT 1

            )

            AND ae.fecha = (

                SELECT de.fecha
                FROM Alumno_Estado de
                WHERE de.id_alumno = ae.id_alumno
                ORDER BY de.fecha DESC
                LIMIT 1

            )

            AND c.id = %s

            ORDER BY a.id DESC

        """, [curso_id])

        columnas = [col[0] for col in cursor.description]

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