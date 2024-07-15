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
        return jsonify({'error': 'Numero no encontrado'})
    contactos = Contacto.query.filter_by(numero_usuario=minumero).all()
    contactos_info = []
    for contacto in contactos:
        contacto_usuario = Cuentausuario.query.filter_by(numero=contacto.numero_contacto).first()
        if contacto_usuario:
            contactos_info.append(f"{contacto.numero_contacto}: {contacto_usuario.nombre}")
    return jsonify(contactos_info), 200

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Crea las tablas en la base de datos si no existen
    app.run(debug=True, host='0.0.0.0', port=5004)
