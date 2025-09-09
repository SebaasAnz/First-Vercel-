from pymongo import MongoClient

client = MongoClient('mongodb+srv://Neider:Nei%40123.@cluster0.4ipvsze.mongodb.net/')
db = client['medicenter']
medicamentos = db['medicamentos']

# Solo insertamos si la colección está vacía
if medicamentos.count_documents({}) == 0:
    medicamentos.insert_many([
        {'nombre': 'Paracetamol', 'dosis': '500mg cada 8 horas'},
        {'nombre': 'Ibuprofeno', 'dosis': '400mg cada 6 horas'},
        {'nombre': 'Amoxicilina', 'dosis': '500mg cada 12 horas'},
        {'nombre': 'Metformina', 'dosis': '850mg cada 12 horas'}
    ])
    print("Medicamentos insertados correctamente.")
else:
    print("Los medicamentos ya existen en la base de datos.")
