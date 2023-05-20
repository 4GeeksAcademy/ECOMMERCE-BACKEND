@app.route('/acompañamiento', methods=['POST'])
def create_acompañamiento():
name = request.json.get('name')
price = request.json.get('price')
description = request.json.get('description')
acompañamiento_type = request.json.get('acompañamiento_type')

acompañamiento = Acompañamiento(name=name, price=price, description=description, acompañamiento_type=acompañamiento_type)
db.session.add(acompañamiento)
db.session.commit()

return jsonify(acompañamiento.serialize()), 201