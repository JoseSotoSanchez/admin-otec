from django.db.models.signals import post_migrate
from django.dispatch import receiver
from django.db import connection
from django.db.utils import ProgrammingError


@receiver(post_migrate)
def create_producto_detalle_view(sender, **kwargs):
    if sender.name == 'administracion':
        print("Se crea la vista detalle_producto para salida de administracion")
        with connection.cursor() as cursor:
            # Eliminar la vista si ya existe
            cursor.execute("DROP VIEW IF EXISTS producto_detalle;")

            # Crear la nueva vista
            cursor.execute("""
                CREATE VIEW producto_detalle AS
                SELECT 
                    p.id,
                    p.codigo_barra,
                    p.nombre AS nombre_producto,
                    p.sku,
                    p.precio_bruto,
                    p.precio_neto,
                    SUM(CASE WHEN s.cantidad_actual > 0 THEN s.cantidad_actual ELSE 0 END) AS stock_actual,
                    MIN(s.fecha_vencimiento) AS fecha_vencimiento
                FROM 
                    inventario_producto p 
                JOIN 
                    inventario_stock s ON p.id = s.id_producto_id
                WHERE 
                    p.es_eliminado = 0
                GROUP BY 
                    p.codigo_barra, p.nombre, p.sku, p.precio_bruto, p.precio_neto;
            """)
            print("producto_detalle Creado o actualizado con exito")

@receiver(post_migrate)
def create_pedidos_view(sender, **kwargs):
    if sender.name == 'administracion':
        print("Se crea la vista pedidos_view para salida de administracion")
        with connection.cursor() as cursor:
            # Eliminar la vista si ya existe
            cursor.execute("DROP VIEW IF EXISTS pedidos_view;")

            # Crear la nueva vista
            cursor.execute("""
                CREATE VIEW pedidos_view AS
                SELECT 
                    pedido.id_pedido as id, 
                    proveedor.nombre as proveedor, 
                    substr(pedido.fecha_recepcion, 9 , 2 ) || '/' ||
                    substr(pedido.fecha_recepcion, 6 , 2 ) || '/' ||
                    substr(pedido.fecha_recepcion, 1 , 4 ) || ' ' ||
                    substr(pedido.fecha_recepcion, 12 , 5 )  as fecha_recepcion,
                    pedido.total_pedido as total_pedido 
                FROM inventario_pedido as pedido 
                    join inventario_proveedor as proveedor on pedido.id_proveedor = proveedor.id
                order by pedido.fecha_recepcion DESC;
            """)
            print("pedidos_view Creado o actualizado con exito")
    

@receiver(post_migrate)
def create_pedidos_productos_view(sender, **kwargs):
    if sender.name == 'administracion':
        print("Se crea la vista pedidos_productos_view para salida de administracion")
        with connection.cursor() as cursor:
            # Eliminar la vista si ya existe
            cursor.execute("DROP VIEW IF EXISTS pedidos_productos_view;")

            # Crear la nueva vista
            cursor.execute("""
                CREATE VIEW pedidos_productos_view AS
                SELECT pedido_producto.id_pedido_id as id_pedido,
                    producto.codigo_barra as codigo_barra ,
                    producto.nombre as nombre_producto, 
                    pedido_producto.cantidad as cantidad,
                    pedido_producto.precio_bruto as precio_producto,
                    pedido_producto.total as precio_total, 
                    producto.precio_bruto as precio_actual_venta 
                FROM inventario_pedidoproducto as pedido_producto 
                    join inventario_producto as producto on producto.id = pedido_producto.id_producto_id;
            """)
            print("pedidos_productos_view Creado o actualizado con exito")

@receiver(post_migrate)
def create_producto_detalle_stock_view(sender, **kwargs):
    if sender.name == 'administracion':
        print("Se crea la vista producto_detalle_stock_view para salida de administracion")
        with connection.cursor() as cursor:
            # Eliminar la vista si ya existe
            cursor.execute("DROP VIEW IF EXISTS producto_detalle_stock_view;")

            # Crear la nueva vista
            cursor.execute("""
                CREATE VIEW producto_detalle_stock_view AS
                SELECT 
                    p.id as id,
                    p.codigo_barra,
                    p.nombre AS nombre_producto,
                    p.precio_bruto as precio_bruto,
                    SUM(CASE WHEN s.cantidad_actual > 0 THEN s.cantidad_actual ELSE 0 END) AS stock_actual,
                    p.stock_critico as stock_critico,
                    SUM(CASE WHEN s.cantidad_actual > 0 THEN s.cantidad_actual ELSE 0 END) - p.stock_critico AS diferencia,
                    MIN(CASE WHEN s.fecha_vencimiento >= DATE('now') THEN s.fecha_vencimiento ELSE 'No registrado' END) AS fecha_proxima_vencimiento
                FROM 
                    inventario_producto p
                JOIN 
                    inventario_stock s ON p.id = s.id_producto_id
                WHERE 
                    p.es_eliminado = 0
                GROUP BY 
                    p.id, p.codigo_barra, p.nombre, p.precio_bruto, p.stock_critico;
            """)
            print("producto_detalle_stock_view Creado o actualizado con exito")



@receiver(post_migrate)
def create_stock_resumen_pedidos_view(sender, **kwargs):
    if sender.name == 'administracion':
        print("Se crea la vista stock_resumen_pedidos_view para salida de administracion")
        with connection.cursor() as cursor:
            # Eliminar la vista si ya existe
            cursor.execute("DROP VIEW IF EXISTS stock_resumen_pedidos_view;")

            # Crear la nueva vista
            cursor.execute("""
                CREATE VIEW stock_resumen_pedidos_view AS
                SELECT 
                    stock.id_producto_id AS id, 
                    proveedor.nombre AS nombre_proveedor, 
                    stock.cantidad_inicial AS stock_compra, 
                    pedido.total_pedido AS total_pedido, 
                    pedido.fecha_recepcion AS fecha_recepcion
                FROM inventario_stock stock
                JOIN inventario_pedido pedido ON pedido.id_pedido = stock.id_pedido_id
                JOIN inventario_proveedor proveedor ON proveedor.id = pedido.id_proveedor
                WHERE strftime('%Y', pedido.fecha_recepcion) = strftime('%Y', 'now')   
                ORDER BY pedido.fecha_recepcion DESC;  

            """)
            print("stock_resumen_pedidos_view Creado o actualizado con exito")
