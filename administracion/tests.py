from django.test import TestCase

# Create your tests here. 
from administracion.models import Producto
from datetime import datetime


class ProductoTestCase(TestCase):
    def setUp(self):
        # Crear 10 productos de prueba
        for i in range(10):
            Producto.objects.create(
                sku=f"SKU-{i}",
                nombre=f"Producto {i}",
                codigo_barra=f"123456789{i}",
                precio_bruto=1000 + i * 10,
                precio_neto=900 + i * 10,
                fecha_creacion=datetime.now(),
                stock_critico=5 + i
            )
    
    def test_producto_count(self):
        # Verificar que se hayan creado 10 productos
        productos_count = Producto.objects.count()
        self.assertEqual(productos_count, 10)
