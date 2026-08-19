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
)

from .services import (
    obtener_aspirantes_por_curso,
    obtener_cursos,
    obtener_cursos_detalle,
    obtener_alumnos_correo_bienvenida,
)

from .emails import enviar_email_bienvenida
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


 
# class InventarioView:
#     def administracion(request):
#         template = loader.get_template("administracion/index.html")
#         return HttpResponse(template.render(request=request))

# Para generar la vista con la tabla si o si debe existir el modelo (usen el verbose)
class AlumnoView(ViewCustom):
  
    @staticmethod
    def get_alumnos():
        return Alumno.objects.filter()#es_eliminado=0)
    
    def get_context_base():
        return {
            "atributos": AlumnoView().get_atributos(Alumno),
            "ids": AlumnoView().get_ids(Alumno),
            "data": AlumnoView().get_alumnos()
        }
 
    def alumnos(request):

        cursos = obtener_cursos()

        curso_id = None
        alumnos = []

        if request.method == "POST":
            curso_id = request.POST.get("id_curso")

            if curso_id:
                alumnos = obtener_aspirantes_por_curso(curso_id)

        context = {
            "cursos": cursos,
            "curso_id": curso_id,
            "title": "Aspirantes",
            "actions_bar": None,
            "ids": ["id"],
            "atributos": [
                "id",
                "nombre",
                "apellido",
                "rut",
                "email",
                "telefono",
                "estado",
                "modificado_por",
                "ingreso",
                "total_pagos"
            ],
            "data": alumnos
        }

        return render(
            request,
            "administracion/alumnos.html",
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

            # DataTables
            "table_order": "desc",

            "atributos": [
                "id",
                "nombre",
                "codigo_curso",
                "fecha_inicio",
                "fecha_fin",
                "dias",
                "horario",
                "costo",
                "modalidad",
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


    # ================================================
    # ACTIVAR / DESACTIVAR
    # ================================================

    @staticmethod
    @require_POST
    def actualizar_estado(request, curso_id):

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

        return redirect("cursos")


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

        context = {
            "title": "Dashboard"
        }

        return render(
            request,
            "administracion/dashboard.html",
            context
        )
    # def ajustar_porcentaje(request): 
    #     porcentaje = request.POST["porcentaje"] 
    #     FileWriter("ganancia.txt", porcentaje).write_new_content() 
    #     context  = ProductosView.get_context_base()
    #     context["porcentaje"] = porcentaje  
    #     return render(request, "administracion/productos.html", context)
    
    # def leer_porcentaje(request): 
    #     if request.method == 'GET': 
    #         current_dir = Path(__file__).parent
    #         ganancia_path = current_dir.parent / 'config' / 'ganancia.txt' 
    #         with open(ganancia_path, 'r') as file:
    #             ganancia = file.read() 
    #         response_data = {
    #             'ganancia': ganancia
    #         }
    #         return JsonResponse(response_data)  
    #     return HttpResponse(status=405)
         
    # def actualizar_producto(request): 
    #     if request.method == 'POST': 
    #         producto_id = request.POST.get('id_producto_update') 
    #         producto = Producto.objects.get(id=producto_id)  
    #         producto.nombre = request.POST.get('nombre_update')
    #         producto.codigo_barra = request.POST.get('codigo_barras_update')
    #         producto.precio_bruto = request.POST.get('precio_final_update')
    #         producto.marca = request.POST.get('marca_update')
    #         producto.unidad_medida = request.POST.get('unidad_medida_update')
    #         producto.precio_neto = request.POST.get('precio_neto_update') 
    #         producto.alerta = True if request.POST.get('alertar_update') == 'on' else False 
    #         producto.stock_critico = request.POST.get('stock_minimo_update') 
    #         producto.save()  
    #         return render(request, "administracion/productos.html", ProductosView.get_context_base())
 
    # def eliminar_producto(request):
    #     if request.method == 'POST':
    #         producto_id = request.POST.get('producto_delete_id')
    #         producto = Producto.objects.get(id=producto_id)
    #         producto.es_eliminado = 1
    #         producto.save()  
    #         return render(request, "administracion/productos.html", ProductosView.get_context_base())
    
    # def agregar_producto(request):
    #     if request.method=="POST": 
    #         # producto.nombre = request.POST.get('nombre_update')
    #         sku="123"
    #         codigo_barra = request.POST.get("codigo_barras")
    #         nombre = request.POST.get("nombre")
    #         precio_neto = request.POST.get('precio_neto')
    #         marca = request.POST.get('marca')
    #         unidad_medida = request.POST.get('stock_minimo') 
    #         alerta = True if request.POST.get('alertar') == 'on' else False 
    #         stock_minimo = request.POST.get('stock_minimo')
    #         unidad_medida = request.POST.get('unidad_medida') 
    #         precio_bruto=  request.POST.get('precio_final') 
    #         prod=Producto.objects.create(sku="123",
    #                                      nombre = nombre,
    #                                      codigo_barra = codigo_barra,
    #                                      precio_bruto = precio_bruto,
    #                                      precio_neto = precio_neto,
    #                                      marca = marca,
    #                                      fecha_creacion = datetime.now(),
    #                                      stock_critico = stock_minimo,
    #                                      unidad_medida = unidad_medida,
    #                                      alerta = alerta) 
    #         prod.save()  
    #         return render(request, "administracion/productos.html", ProductosView.get_context_base())
    

# class ProveedoresView(ViewCustom):
  
#     @staticmethod
#     def get_proveedores():  
#         return Proveedor.objects.filter(es_eliminado=False)
    
#     def get_context_base():
#         return {
#             "atributos": ProveedoresView().get_atributos(Proveedor),
#             "ids": ProveedoresView().get_ids(Proveedor),
#             "data": ProveedoresView().get_proveedores()
#         }
          
#     def proveedores(request): 
#         return render(request, "administracion/proveedores.html", ProveedoresView.get_context_base())

    
#     def agregar_proveedor(request): 
#         nuevo_proveedor = Proveedor(
#             nombre=request.POST.get("nombre"),
#             telefono=request.POST.get("telefono"),
#             email=request.POST.get("email"),
#             direccion=request.POST.get("direccion"),
#             es_eliminado=False
#         ) 
#         nuevo_proveedor.save()  
#         return render(request, "administracion/proveedores.html", ProveedoresView.get_context_base())
    
#     def actualizar_proveedor(request):
#         if request.method == "POST":
#             proveedor_id = request.POST.get("id_proveedor")
#             proveedor = Proveedor.objects.get(id=proveedor_id)
#             proveedor.nombre = request.POST.get("nombre")
#             proveedor.telefono = request.POST.get("telefono")
#             proveedor.email = request.POST.get("email")
#             proveedor.direccion = request.POST.get("direccion")
#             proveedor.save()   
#             return render(request, "administracion/proveedores.html", ProveedoresView.get_context_base())
        
#     def eliminar_proveedor(request):
#         if request.method == "POST":
#             proveedor_id = request.POST.get("id_proveedor_eliminar")
#             proveedor = Proveedor.objects.get(id=proveedor_id)
#             proveedor.es_eliminado = True 
#             proveedor.save()
#             return render(request, "administracion/proveedores.html", ProveedoresView.get_context_base())


# class SalidaInventarioView(ViewCustom):

#     @staticmethod
#     def get_stock():  
#         return ProductoDetalle.objects.all()
    
#     @staticmethod
#     def get_tipo_salida():
#         return TipoSalida.objects.all()
    
#     def get_context_base_pedidos():
#         return {
#             "tipo_salida": SalidaInventarioView().get_tipo_salida()
#         }
    
#     # Método para devolver el detalle de los productos en formato JSON
#     #SOLO PRODCUTOS QUE CUENTEN CON STOCK EN BASE DE DATOS SUM(STOCK BY PRODUCTO)
#     #MIRAR LA VISTA
#     def detalle_producto_json(request): 
#         productos = SalidaInventarioView.get_stock()
#         # Convertir productos a una lista de diccionarios
#         data = [
#             {
#                 "id": producto.id,
#                 "sku": producto.sku,
#                 "codigo_barra": producto.codigo_barra,
#                 "nombre_producto": producto.nombre_producto, 
#                 "precio_bruto": producto.precio_bruto,
#                 "precio_neto": producto.precio_neto,   
#                 "stock_actual": producto.stock_actual,
#                 "fecha_vencimiento": producto.fecha_vencimiento.isoformat() if producto.fecha_vencimiento else None, 
#             }
#             for producto in productos
#         ]
#         return JsonResponse(data, safe=False)
    
    
#     @staticmethod
#     def decrementar_stock(id_producto, cantidad_comprada):
#         with transaction.atomic():
#             # Obtener todos los stocks disponibles ordenados por fecha de vencimiento
#             stocks = Stock.objects.filter(id_producto=id_producto, cantidad_actual__gt=0).order_by('fecha_vencimiento')
            
#             for stock in stocks:
#                 # Verificar si ya no queda cantidad por decrementar
#                 if cantidad_comprada <= 0:
#                     break
                
#                 # Si la cantidad disponible en el stock es mayor o igual a la cantidad que se quiere comprar
#                 if stock.cantidad_actual >= cantidad_comprada:
#                     stock.cantidad_actual -= cantidad_comprada
#                     stock.save()
#                     cantidad_comprada = 0  # Deja de comprar, ya no hay cantidad pendiente
#                 else:
#                     # Si la cantidad disponible en este stock no es suficiente
#                     cantidad_comprada -= stock.cantidad_actual
#                     stock.cantidad_actual = 0  # Se agota el stock actual
#                     stock.save()
 
    
 
#     @staticmethod
#     def registrar_venta(producto, cantidad):
#         SalidaInventarioView.decrementar_stock(producto.id, cantidad)
    
    
#     def salida_inventario(request):
#         return render(request, "administracion/salida_inventario.html", SalidaInventarioView.get_context_base_pedidos())
    
#     @csrf_exempt
#     def send_salida_inventario_json(request):
#         query_dict = request.POST
#         json_data = list(query_dict.keys())[0]
        
#         try:
#             products = json.loads(json_data)

#             model_tipo_salida = TipoSalida.objects.get(tipo=products['tipo_salida'])
#             model_salida_inventario = SalidaInventario(id_tipo_salida=model_tipo_salida, fecha_salida=datetime.now())
#             model_salida_inventario.save()

#             for salidas in products['productos_carrito']:
#                 producto = Producto.objects.get(codigo_barra=salidas['codigo_barra'])
#                 #decrementar
#                 SalidaInventarioView.decrementar_stock(producto,int(salidas['cantidad_comprar']))
#                 model_producto_salida_inventario = ProductoSalidaInventario(
#                     id_salida_inventario=model_salida_inventario,
#                     id_producto=producto,
#                     cantidad=salidas['cantidad_comprar'],
#                     precio_bruto=salidas['precio_bruto'],
#                     sub_total=salidas['precio_neto']
#                 )
#                 model_producto_salida_inventario.save()
              
#             return JsonResponse({'success': 'Salida de administracion registrada exitosamente.'}, status=201)
#         except json.JSONDecodeError:
#             return JsonResponse({'error': 'Error en terminar la salida de administracion.'}, status=400)



# class PedidosView(ViewCustom):
  
#     @staticmethod
#     def get_pedidos():  
#         return Pedido.objects.all()
    
#     def get_context_base_pedidos():
#         return {
#             "atributos": PedidosView().get_atributos(PedidosTableView),
#             "data": PedidosTableView.objects.all(), 
#             "ids": PedidosView().get_ids(PedidosTableView), 
#         }
    
#     def get_context_base():
#         return {
#             "atributos": PedidosView().get_atributos(Pedido),
#             "data": PedidosView().get_pedidos(),
#             "atributosProductos": ProductosView().get_atributos(Producto),
#             "ids": PedidosView().get_ids(Pedido),
#             "pedidos": PedidosView().get_pedidos(),
#             "productos": ProductosView().get_productos(),
#             "proveedores": ProveedoresView().get_proveedores()
#         }
    
#     def lista_pedidos(request):  
#         return render(request, "administracion/lista_pedidos.html", PedidosView.get_context_base_pedidos())
    
#     def get_productos_by_pedido_json(request, id_pedido): 
#         productos_by_pedido = PedidosProductosView.objects.filter(id_pedido = id_pedido)
#         data = [
#             {  
#                 "codigo_barra": producto.codigo_barra,
#                 "nombre_producto": producto.nombre_producto, 
#                 "precio_producto": producto.precio_producto,
#                 "cantidad": producto.cantidad,   
#                 "precio_total": producto.precio_total,
#                 "precio_actual_venta": producto.precio_actual_venta, 
#             }
#             for producto in productos_by_pedido
#         ]
#         return JsonResponse(data, safe=False)

#     @staticmethod
#     def crear_pedido(request):
#         if request.method == 'POST':  
#             try:
#                 data = json.loads(request.body)
#                 proveedor_id = data.get('proveedor')
#                 productos = data.get('productos')
#                 total_pedido = data.get('total_pedido')
#                 fecha_recepcion = datetime.now()
#                 pedido = Pedido.objects.create(
#                     id_proveedor=proveedor_id,
#                     fecha_recepcion=str(fecha_recepcion),
#                     total_pedido=str(total_pedido)
#                 )
#                 for producto_data in productos:
#                     PedidosView.agregar_pedido_producto(pedido, producto_data)
#                 return JsonResponse({'success': True})
                
#             except Producto.DoesNotExist:
#                 return JsonResponse({'success': False, 'error': 'Producto no encontrado'}, status=400)
#             except Exception as e:
#                 return JsonResponse({'success': False, 'error': str(e)}, status=400)
#         return JsonResponse({'success': False, 'error': 'Invalid request'}, status=400)
    
#     def agregar_pedido_producto(pedido, producto_data):
#         codigo_barra = producto_data['codigoBarra']
#         cantidad = producto_data['cantidad']
#         valor_neto = producto_data['valorNeto']
#         ganancia = producto_data['ganancia']
#         iva = producto_data['iva']
#         precioVenta = producto_data['precioVenta']
#         precio_bruto = valor_neto + ganancia + iva
#         total = precio_bruto * cantidad - (ganancia * cantidad)
#         producto = Producto.objects.filter(codigo_barra = codigo_barra)[0]
#         pedido_producto = PedidoProducto.objects.create(
#             id_pedido_id=pedido.id_pedido,
#             id_producto_id=producto.id,
#             cantidad=cantidad,
#             precio_bruto=precio_bruto - ganancia,
#             total=total
#         )
#         if producto.precio_neto != valor_neto or producto.precio_bruto != precioVenta:
#             producto.precio_neto = valor_neto
#             producto.precio_bruto = precioVenta
#             producto.save()
#         PedidosView.agregar_stock(producto, pedido, cantidad)

#     def agregar_stock(producto, pedido, cantidad):
#         stock, created = Stock.objects.get_or_create(
#                         id_producto=producto,
#                         id_pedido=pedido,
#                         defaults={
#                             'cantidad_inicial': cantidad,
#                             'cantidad_actual': cantidad,
#                             'fecha_vencimiento': date.today() 
#                         }
#                     )
#         if not created:
#                         stock.cantidad_actual += cantidad
#                         stock.save()

#     def pedidos(request): 
#        return render(request, "administracion/pedidos.html", PedidosView.get_context_base())

# class StockView(ViewCustom):
    
#     @staticmethod
#     def get_stock_resumen():
#         return ProductoDetalleStockView.objects.all()
    
#     def get_context_base():
#         return {
#             "atributos": StockView().get_atributos(ProductoDetalleStockView),
#             "ids": StockView().get_ids(ProductoDetalleStockView),
#             "data": StockView().get_stock_resumen()
#         }
 
#     def stock_resumen(request): 
#         context = StockView.get_context_base()
#         return render(request, "administracion/stock_resumen.html", context)
    
#     def stock_pedidos_by_producto_json(request, id_producto):  
#         stock_by_pedido = StockResumenPedidosView.objects.filter(id=id_producto).order_by('-fecha_recepcion')[:20]
#         data = [
#             {   
#                 "nombre_proveedor": pedido.nombre_proveedor, 
#                 "stock_compra": pedido.stock_compra,
#                 "total_pedido": pedido.total_pedido,
#                 "fecha_recepcion": pedido.fecha_recepcion
#             }
#             for pedido in stock_by_pedido
#         ]
#         return JsonResponse(data, safe=False)

# def DashboardView(request):
#     locale.setlocale(locale.LC_TIME, 'es_ES.UTF-8')
#     cursor = connection.cursor()

#     #Selecciona los 10 pedidos con el valor total más alto del último mes
#     cursor.execute(
#         """
#         SELECT * 
#         from (SELECT sum(ppv.precio_total) as precio_total, sum(ppv.cantidad), id_pedido, date(fecha_recepcion)
#         FROM (  SELECT 	pp.total as precio_total,
#                         pp.cantidad,
#                         ip.id_pedido,
#                         ip.fecha_recepcion
#                 FROM 	inventario_pedidoproducto pp
#                 JOIN 	inventario_producto pr on pr.id = pp.id_producto_id
#                 JOIN	inventario_pedido ip ON ip.id_pedido = pp.id_pedido_id 
#                 WHERE 	ip.fecha_recepcion BETWEEN datetime('now', 'localtime', '-1 month') AND datetime('now', 'localtime')) ppv
#         GROUP BY ppv.id_pedido
#         ORDER BY sum(ppv.precio_total) DESC 
#         LIMIT 10)
#         order by id_pedido;
#         """)
    
#     id_pedido = []
#     cantidad = []
#     precio_total = []
#     fecha_recepcion = []
#     for row in cursor.fetchall():
#         result_dict = {
#             'precio_total':     row[0],
#             'cantidad':         row[1],
#             'id_pedido':        row[2],
#             'fecha_recepcion':  datetime.strptime(row[3], "%Y-%m-%d").strftime("%a %d de %b")  
#         }
#         id_pedido.append(result_dict['id_pedido'])
#         cantidad.append(result_dict['cantidad'])
#         precio_total.append(result_dict['precio_total'])
#         fecha_recepcion.append(result_dict['fecha_recepcion'])

#     #Selecciona los tipos de salida con count de cada grupo
#     cursor.execute(
#         """
#         SELECT ts.tipo AS tipo_salida, count(*) as cantidad_salida
#         FROM inventario_producto pr JOIN inventario_productosalidainventario ps ON pr.id = ps.id_producto_id
#         JOIN inventario_salidainventario si ON si.id = ps.id_salida_inventario_id
#         JOIN inventario_tiposalida ts ON ts.id = si.id_tipo_salida_id
#         GROUP BY si.id_tipo_salida_id 
#         """)

#     tipo_salida = []
#     cantidad_salida = []
#     for row in cursor.fetchall():
#         result_dict = {
#             'tipo_salida':      row[0],
#             'cantidad_salida':  row[1]
#         }
#         tipo_salida.append(result_dict['tipo_salida'])
#         cantidad_salida.append(result_dict['cantidad_salida'])
    
#     #Selecciona los 10 productos mas vendidos del último mes
#     cursor.execute(
#         """
#         SELECT pr.id as id_producto, count(*) as numero_productos, pr.nombre as nombre_producto, COUNT(*) * pr.precio_bruto as valor_venta
#         FROM inventario_producto pr JOIN inventario_productosalidainventario ps ON pr.id = ps.id_producto_id
#         JOIN inventario_salidainventario si ON si.id = ps.id_salida_inventario_id
#         JOIN inventario_tiposalida ts ON ts.id = si.id_tipo_salida_id
#         WHERE ts.tipo = 'Venta'
#         AND si.fecha_salida BETWEEN datetime('now', 'localtime', '-1 month') AND datetime('now', 'localtime')
#         group by pr.id
#         order by nombre_producto
#         limit 10
#         """)
    
#     id_producto = []
#     numero_productos = []
#     nombre_producto = []
#     valor_venta = []
#     for row in cursor.fetchall():
#         result_dict = {
#             'id_producto':      row[0],
#             'numero_productos': row[1],
#             'nombre_producto':  row[2],
#             'valor_venta':      row[3]
#         }
#         id_producto.append(result_dict['id_producto'])
#         numero_productos.append(result_dict['numero_productos'])
#         nombre_producto.append(result_dict['nombre_producto'])
#         valor_venta.append(result_dict['valor_venta'])

#     #Selecciona los 10 productos mas vendidos de los últimos 3 meses
#     cursor.execute(
#         """
#         SELECT pr.id as id_producto, count(*) as numero_productos, pr.nombre as nombre_producto, COUNT(*) * pr.precio_bruto as valor_venta
#         FROM inventario_producto pr JOIN inventario_productosalidainventario ps ON pr.id = ps.id_producto_id
#         JOIN inventario_salidainventario si ON si.id = ps.id_salida_inventario_id
#         JOIN inventario_tiposalida ts ON ts.id = si.id_tipo_salida_id
#         WHERE ts.tipo = 'Venta'
#         AND si.fecha_salida BETWEEN datetime('now', 'localtime', '-3 month') AND datetime('now', 'localtime')
#         group by pr.id
#         order by nombre_producto
#         limit 10
#         """)
    
#     id_producto_3mes = []
#     numero_productos_3mes = []
#     nombre_producto_3mes = []
#     valor_venta_3mes = []
#     for row in cursor.fetchall():
#         result_dict = {
#             'id_producto_3mes':      row[0],
#             'numero_productos_3mes': row[1],
#             'nombre_producto_3mes':  row[2],
#             'valor_venta_3mes':      row[3]
#         }
#         id_producto_3mes.append(result_dict['id_producto_3mes'])
#         numero_productos_3mes.append(result_dict['numero_productos_3mes'])
#         nombre_producto_3mes.append(result_dict['nombre_producto_3mes'])
#         valor_venta_3mes.append(result_dict['valor_venta_3mes'])

#     #Selecciona top 10 proveedores con mayor cantidad de pedidos del ultimo año
#     cursor.execute(
#         """
#         select numero_pedidos, id_proveedor, nombre_proveedor
#         from (select count(*) as numero_pedidos, pv.id as id_proveedor, pv.nombre as nombre_proveedor
#         from inventario_pedido pe 
#         join inventario_proveedor pv on pe.id_proveedor = pv.id
#         where pe.fecha_recepcion BETWEEN datetime('now', 'localtime', '-1 year') AND datetime('now', 'localtime')
#         group by  pv.id
#         order by numero_pedidos DESC 
#         limit 10)
#         order by nombre_proveedor;
#         """)

#     numero_pedidos = []
#     id_proveedor = []
#     nombre_proveedor = []
#     for row in cursor.fetchall():
#         result_dict = {
#             'numero_pedidos':           row[0],
#             'id_proveedor':             row[1],
#             'nombre_proveedor':         row[2]
#         }
#         numero_pedidos.append(result_dict['numero_pedidos'])
#         id_proveedor.append(result_dict['id_proveedor'])
#         nombre_proveedor.append(result_dict['nombre_proveedor'])
    
#     #Selecciona top 10 proveedores con mayor valor todal de pedidos del ultimo año
#     cursor.execute(
#         """
#         select total_pedidos, id_proveedor, nombre_proveedor
#         from (select sum(pe.total_pedido) as total_pedidos, pv.id as id_proveedor, pv.nombre as nombre_proveedor
#         from inventario_pedido pe 
#         join inventario_proveedor pv on pe.id_proveedor = pv.id
#         where pe.fecha_recepcion BETWEEN datetime('now', 'localtime', '-1 year') AND datetime('now', 'localtime')
#         group by  pv.id
#         order by total_pedidos DESC
#         limit 10)
#         order by nombre_proveedor;
#         """)

#     total_pedidos = []
#     id_proveedor2 = []
#     nombre_proveedor2 = []
#     for row in cursor.fetchall():
#         result_dict = {
#             'total_pedidos':        row[0],
#             'id_proveedor2':        row[1],
#             'nombre_proveedor2':    row[2]
#         }
#         total_pedidos.append(result_dict['total_pedidos'])
#         id_proveedor2.append(result_dict['id_proveedor2'])
#         nombre_proveedor2.append(result_dict['nombre_proveedor2'])

#     top_metricas = []
#     # Cantidad de ventas anuales
#     query_ventas = """
#     SELECT count(*)
#     FROM inventario_productosalidainventario producto
#     JOIN inventario_salidainventario salida ON salida.id = producto.id_salida_inventario_id
#     WHERE strftime('%Y', fecha_salida) = strftime('%Y', 'now')
#     AND id_tipo_salida_id = 1;
#     """

#     cursor.execute(query_ventas)
#     ventas_anuales = cursor.fetchone()[0]
#     top_metricas.append(ventas_anuales)

#     # Cantidad de productos vendidos anuales
#     query_sum_productos = """
#     SELECT sum(cantidad)
#     FROM inventario_productosalidainventario producto
#     JOIN inventario_salidainventario salida ON salida.id = producto.id_salida_inventario_id
#     WHERE strftime('%Y', fecha_salida) = strftime('%Y', 'now')
#     AND id_tipo_salida_id = 1;
#     """

#     cursor.execute(query_sum_productos)
#     productos_anuales = cursor.fetchone()[0]  # Obtener el resultado como un número
#     top_metricas.append(productos_anuales)
    
#     # Cantidad de productos vendidos anuales
#     query_precio = """
#     SELECT sum(precio_bruto)
#     FROM inventario_productosalidainventario producto
#     JOIN inventario_salidainventario salida ON salida.id = producto.id_salida_inventario_id
#     WHERE strftime('%Y', fecha_salida) = strftime('%Y', 'now')
#     AND id_tipo_salida_id = 1;
#     """

#     cursor.execute(query_precio)
#     precio_productos = cursor.fetchone()[0]  # Obtener el resultado como un número
#     top_metricas.append(precio_productos)  
    

    
#     # Cantidad de productos vendidos anuales
#     query_precio = """
#         SELECT 
#             producto.id_producto_id,
#             SUM(producto.cantidad) AS total_vendido,
#             inventario_producto.nombre as producto
#         FROM 
#             inventario_productosalidainventario producto
#         JOIN 
#             inventario_salidainventario salida ON salida.id = producto.id_salida_inventario_id
#         JOIN 
#             inventario_producto ON producto.id_producto_id = inventario_producto.id
#         WHERE 
#             strftime('%Y', salida.fecha_salida) = strftime('%Y', 'now')
#             AND salida.id_tipo_salida_id = 1
#         GROUP BY 
#             producto.id_producto_id, inventario_producto.nombre
#         ORDER BY 
#             total_vendido DESC
#         LIMIT 1;
#     """

#     cursor.execute(query_precio)

#     top_producto = []  
#     for row in cursor.fetchall():
#         result_dict = {
#             'total_vendido': row[1],
#             'producto':      row[2],
#         }
#         top_producto.append(result_dict['total_vendido'])
#         top_producto.append(result_dict['producto']) 

#     top_metricas.append(top_producto)  
    
#     context = {
#         'precio_total':             json.dumps(precio_total),
#         'cantidad':                 json.dumps(cantidad),
#         'id_pedido':                json.dumps(id_pedido),
#         'fecha_recepcion':          json.dumps(fecha_recepcion),
#         'tipo_salida':              json.dumps(tipo_salida),
#         'cantidad_salida':          json.dumps(cantidad_salida),
#         'id_producto':              json.dumps(id_producto),
#         'numero_productos':         json.dumps(numero_productos),
#         'nombre_producto':          json.dumps(nombre_producto),
#         'valor_venta':              json.dumps(valor_venta),
#         'id_producto_3mes':         json.dumps(id_producto_3mes),
#         'numero_productos_3mes':    json.dumps(numero_productos_3mes),
#         'nombre_producto_3mes':     json.dumps(nombre_producto_3mes),
#         'valor_venta_3mes':         json.dumps(valor_venta_3mes),
#         'numero_pedidos':           json.dumps(numero_pedidos),
#         'id_proveedor':             json.dumps(id_proveedor),
#         'nombre_proveedor':         json.dumps(nombre_proveedor),
#         'total_pedidos':            json.dumps(total_pedidos),
#         'id_proveedor2':            json.dumps(id_proveedor2),
#         'nombre_proveedor2':        json.dumps(nombre_proveedor2), 
#         'top_metricas':             json.dumps(top_metricas)
#     }
#     return render(request, "administracion/dashboard.html", context)
