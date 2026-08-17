from django.urls import path
from .views import AlumnoView #,  ProveedoresView, SalidaInventarioView, PedidosView, StockView, DashboardView


urlpatterns = [
    path('', AlumnoView.alumnos, name="alumnos"),
    path('alumnos', AlumnoView.alumnos, name="alumnos"),
    # path('ajustar_porcentaje', ProductosView.ajustar_porcentaje, name="productos"),
    # path('leer_porcentaje', ProductosView.leer_porcentaje, name="productos"),
    # path('actualizar_producto', ProductosView.actualizar_producto, name="productos"),
    # path('eliminar_producto', ProductosView.eliminar_producto, name="productos"),
    # path('guardar_producto', ProductosView.agregar_producto, name="productos"),
    # path('proveedores', ProveedoresView.proveedores, name="proveedores"),
    # path('agregar_proveedor', ProveedoresView.agregar_proveedor , name="proveedores"),
    # path('actualizar_proveedor', ProveedoresView.actualizar_proveedor , name="proveedores"),
    # path('eliminar_proveedor', ProveedoresView.eliminar_proveedor , name="proveedores"),
    # path('salida_inventario', SalidaInventarioView.salida_inventario, name="salida_inventario"),
    # path('detalle_producto_json', SalidaInventarioView.detalle_producto_json, name="salida_inventario"),
    # path('pedidos', PedidosView.pedidos , name="pedidos"),
    # path('productos', ProductosView.get_productos , name="pedidos"),
    # path('send_salida_inventario_json', SalidaInventarioView.send_salida_inventario_json , name="send_salida_inventario_json"),
    # path('lista_pedidos', PedidosView.lista_pedidos , name="pedidos"),
    # path('get_productos_by_pedido_json/<int:id_pedido>', PedidosView.get_productos_by_pedido_json , name="pedidos"), 
    # path('productos', ProductosView.get_productos , name="pedidos"),
    # path('crear_pedido', PedidosView.crear_pedido, name="crear_pedido"),
    # path('stock', StockView.stock_resumen, name="stock"),
    # path('stock_pedidos_by_producto_json/<int:id_producto>', StockView.stock_pedidos_by_producto_json , name="stock"),
    # path('dashboard', DashboardView, name="dashboard")
    
]
