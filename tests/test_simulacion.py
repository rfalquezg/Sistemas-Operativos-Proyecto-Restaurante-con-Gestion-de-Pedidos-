import unittest
from simulacion import ejecutar_simulacion


class PruebasSimulacion(unittest.TestCase):
    def test_cuatro_versiones(self):
        for tipo in ("basico", "complejo"):
            for con_mutex in (False, True):
                with self.subTest(tipo=tipo, con_mutex=con_mutex):
                    r = ejecutar_simulacion(tipo, con_mutex, 2, 1)
                    self.assertEqual(r["stock_final"], 0)
                    self.assertEqual(r["reservas"], 1 if con_mutex else 2)
                    self.assertEqual(r["conflicto"], not con_mutex)
                    self.assertEqual(len(r["movimientos"]), 2)
                    for m in r["movimientos"]:
                        self.assertIn("hilo", m)
                        self.assertIn("operacion", m)
                        self.assertIn("antes", m)
                        self.assertIn("resultado", m)
                        self.assertIn("despues", m)

    def test_mas_cocineros(self):
        r = ejecutar_simulacion("complejo", True, 5, 2)
        self.assertEqual(r["reservas"], 2)
        self.assertEqual(r["stock_final"], 0)
        self.assertFalse(r["conflicto"])

    def test_actualizaciones_perdidas(self):
        r = ejecutar_simulacion("basico", False, 3, 4)
        self.assertEqual(r["reservas"], 3)
        self.assertEqual(r["stock_final"], 3)
        self.assertTrue(r["conflicto"])

    def test_sin_existencias(self):
        r = ejecutar_simulacion("basico", True, 2, 0)
        self.assertEqual(r["reservas"], 0)
        self.assertFalse(r["conflicto"])

    def test_parametros_invalidos(self):
        with self.assertRaises(ValueError):
            ejecutar_simulacion("basico", False, 1, 1)
        with self.assertRaises(ValueError):
            ejecutar_simulacion("complejo", False, 2, -1)


if __name__ == "__main__":
    unittest.main()
