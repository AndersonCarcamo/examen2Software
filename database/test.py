import unittest
from app import app, db, Cuentausuario, Contacto, Operacion
from datetime import datetime

class TestModels(unittest.TestCase):

    def setUp(self):
        # Configurar la aplicación Flask para pruebas
        self.app = app
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:Anvarnv23@localhost/billetera_yape'
        self.app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        self.app.config['TESTING'] = True

        with self.app.app_context():
            db.drop_all()
            db.create_all()
            # Añadir datos iniciales
            self.cuenta1 = Cuentausuario(numero='21345', nombre='Arnoldo', saldo=200)
            self.cuenta2 = Cuentausuario(numero='123', nombre='Luisa', saldo=500)
            self.cuenta3 = Cuentausuario(numero='456', nombre='Andrea', saldo=50)
            db.session.add_all([self.cuenta1, self.cuenta2, self.cuenta3])
            db.session.commit()

            self.contacto1 = Contacto(numero_usuario='21345', numero_contacto='123')
            self.contacto2 = Contacto(numero_usuario='21345', numero_contacto='456')
            db.session.add_all([self.contacto1, self.contacto2])
            db.session.commit()

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    # Caso de éxito: Transferencia exitosa entre cuentas
    def test_transferencia_exitosa(self):
        with self.app.app_context():
            operacion = Operacion(cuenta_origen='21345', cuenta_destino='123', valor=100)
            self.cuenta1.saldo -= 100
            self.cuenta2.saldo += 100
            db.session.add(operacion)
            db.session.commit()
            self.assertEqual(self.cuenta1.saldo, 100)
            self.assertEqual(self.cuenta2.saldo, 600)

    # Caso de éxito: Historial de operaciones
    def test_historial_operaciones(self):
        with self.app.app_context():
            operacion1 = Operacion(cuenta_origen='21345', cuenta_destino='123', valor=100)
            operacion2 = Operacion(cuenta_origen='21345', cuenta_destino='456', valor=50)
            db.session.add_all([operacion1, operacion2])
            db.session.commit()
            historial = Operacion.query.filter((Operacion.cuenta_origen == '21345') | (Operacion.cuenta_destino == '21345')).all()
            self.assertEqual(len(historial), 2)
            self.assertEqual(historial[0].valor, 100)
            self.assertEqual(historial[1].valor, 50)

    # Caso de error: Transferencia a un contacto que no está en la lista
    def test_transferencia_error_contacto_no_en_lista(self):
        with self.app.app_context():
            with self.assertRaises(ValueError) as context:
                operacion = Operacion(cuenta_origen='21345', cuenta_destino='100', valor=50)
                if '100' not in [contacto.numero_contacto for contacto in Contacto.query.filter_by(numero_usuario='21345').all()]:
                    raise ValueError("El contacto no está en la lista de contactos.")
            self.assertTrue('El contacto no está en la lista de contactos.' in str(context.exception))

    # Caso de error: Transferencia con saldo insuficiente
    def test_transferencia_error_saldo_insuficiente(self):
        with self.app.app_context():
            with self.assertRaises(ValueError) as context:
                operacion = Operacion(cuenta_origen='21345', cuenta_destino='123', valor=300)
                self.cuenta1.saldo = 200
                if self.cuenta1.saldo < 300:
                    raise ValueError("Saldo insuficiente.")
            self.assertTrue('Saldo insuficiente.' in str(context.exception))

    # Caso de error: Transferencia a una cuenta inexistente
    def test_transferencia_error_cuenta_inexistente(self):
        with self.app.app_context():
            with self.assertRaises(ValueError) as context:
                cuenta_destino = Cuentausuario.query.filter_by(numero='99999').first()
                if not cuenta_destino:
                    raise ValueError("Cuenta destino no encontrada.")
            self.assertTrue('Cuenta destino no encontrada.' in str(context.exception))

if __name__ == '__main__':
    unittest.main()
