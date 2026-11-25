import unittest
from simulacion import ejecutar_simulacion


class PruebasKitchenLab(unittest.TestCase):
    def test_cuatro_escenarios(self):
        for tipo in ('basico', 'complejo'):
            for mutex in (False, True):
                with self.subTest(tipo=tipo, mutex=mutex):
                    r = ejecutar_simulacion(tipo, mutex, 2, 1)
                    self.assertEqual(r['stock_final'], 0)
                    self.assertEqual(r['reservas'], 1 if mutex else 2)
                    self.assertEqual(r['conflictos'], 0 if mutex else 1)
                    self.assertEqual(r['conflicto'], not mutex)
                    self.assertGreaterEqual(len(r['movimientos']), 6)
                    self.assertTrue(all('hilo' in m and 'etapa' in m and
                                        'antes' in m and 'despues' in m for m in r['movimientos']))

    def test_stock_cero(self):
        for mutex in (True, False):
            r = ejecutar_simulacion('basico', mutex, 2, 0)
            self.assertEqual(r['reservas'], 0)
            self.assertFalse(r['conflicto'])
            self.assertEqual(r['rechazados'], 2)

    def test_stock_varias_unidades(self):
        r = ejecutar_simulacion('complejo', True, 5, 3)
        self.assertEqual(r['reservas'], 3)
        self.assertEqual(r['stock_final'], 0)
        self.assertFalse(r['conflicto'])
        r = ejecutar_simulacion('complejo', False, 3, 4)
        self.assertEqual(r['reservas'], 3)
        self.assertEqual(r['stock_final'], 3)
        self.assertEqual(r['conflictos'], 2)

    def test_validacion(self):
        for args in [('otro', False, 2, 1), ('basico', False, 1, 1),
                     ('basico', True, 2, -1)]:
            with self.assertRaises(ValueError):
                ejecutar_simulacion(*args)

if __name__ == '__main__':
    unittest.main()
