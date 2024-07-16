from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_cors import CORS

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:Anvarnv23@localhost/billetera_yape'
db = SQLAlchemy(app)

CORS(app, resources={r"/*": {"origins": "*"}})

class Cuentausuario(db.Model):
    __tablename__ = 'cuentausuario'
    numero = db.Column(db.String(9), primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    saldo = db.Column(db.Integer, nullable=False)

class Contacto(db.Model):
    __tablename__ = 'contacto'
    id = db.Column(db.Integer, primary_key=True)
    numero_usuario = db.Column(db.String(9), db.ForeignKey('cuentausuario.numero'), nullable=False)
    numero_contacto = db.Column(db.String(9), db.ForeignKey('cuentausuario.numero'), nullable=False)
    __table_args__ = (db.UniqueConstraint('numero_usuario', 'numero_contacto', name='_cuenta_contacto_uc'),)

class Operacion(db.Model):
    __tablename__ = 'operacion'
    id = db.Column(db.Integer, primary_key=True)
    cuenta_origen = db.Column(db.String(9), db.ForeignKey('cuentausuario.numero'), nullable=False)
    cuenta_destino = db.Column(db.String(9), db.ForeignKey('cuentausuario.numero'), nullable=False)
    valor = db.Column(db.Integer, nullable=False)
    fecha = db.Column(db.DateTime, default=datetime.utcnow)

@app.route('/billetera/contactos', methods=['GET'])
def listar_contactos():
    minumero = request.args.get('minumero')
    numero = Cuentausuario.query.filter_by(numero=minumero).first()
    if not numero:
        return jsonify({'error': 'Numero no encontrado'}), 404
    contactos = Contacto.query.filter_by(numero_usuario=minumero).all()
    contactos_info = []
    for contacto in contactos:
        contacto_usuario = Cuentausuario.query.filter_by(numero=contacto.numero_contacto).first()
        if contacto_usuario:
            contactos_info.append(f"{contacto.numero_contacto}: {contacto_usuario.nombre}")
    return jsonify(contactos_info), 200

@app.route('/billetera/pagar', methods=['GET'])
def pagar():
    minumero = request.args.get('minumero')
    numero_destino = request.args.get('numerodestino')
    valor = int(request.args.get('valor'))
    cuenta_origen = Cuentausuario.query.filter_by(numero = minumero).first()
    if not cuenta_origen:
        return jsonify({'error': 'Este numero no existe'}), 404
    cuenta_destino = Cuentausuario.query.filter_by(numero=numero_destino).first()
    if not cuenta_destino:
        return jsonify({'error': 'Numero destino no existe'}), 400
    if cuenta_origen.saldo < valor:
        return jsonify({'error': 'Saldo insuficiente'}), 400
    # descuenta el saldo en la cuenta de origen
    cuenta_origen.saldo -= valor
    # aumenta el saldo en la cuenta de destino
    cuenta_destino.saldo += valor
    operacion = Operacion(cuenta_origen=minumero, cuenta_destino=numero_destino, valor=valor)
    db.session.add(operacion)
    db.session.commit()
    return jsonify({'operacion': 'Operacion realizada con exito', 'fecha': operacion.fecha}), 200

@app.route('/billetera/historial', methods=['GET'])
def historial_operaciones():
    minumero = request.args.get('minumero')
    cuentausuario = Cuentausuario.query.filter_by(numero=minumero).first()
    if not cuentausuario:
        return jsonify({'error': 'Este numero no existe'}), 404
    saldo_actual = cuentausuario.saldo
    operaciones_realizadas = Operacion.query.filter_by(cuenta_origen=minumero).all()
    operaciones_recibidas = Operacion.query.filter_by(cuenta_destino=minumero).all()
    operaciones_info = []
    for operacion in operaciones_realizadas:
        cuenta_destino = Cuentausuario.query.filter_by(numero=operacion.cuenta_destino).first()
        operaciones_info.append(f"Pago realizado de {operacion.valor} a {cuenta_destino.nombre}")
    for operacion in operaciones_recibidas:
        cuenta_origen = Cuentausuario.query.filter_by(numero=operacion.cuenta_origen).first()
        operaciones_info.append(f"Pago recibido de {operacion.valor} de {cuenta_origen.nombre}")
    return jsonify({'saldo': saldo_actual, 'operaciones': operaciones_info}), 200


if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Crea las tablas en la base de datos si no existen
    app.run(debug=True, host='0.0.0.0', port=5004)
