from flask import Flask, request, render_template, jsonify
import json
from organizer.Modelo import distribuicao_graduacao as dg
from organizer.Estruturas_de_Dados import array_manipulator as am
import os


app = Flask(__name__)
mydg = dg()
myam = am()

@app.route('/', methods=['GET'])
def index():
    return render_template('upload.html')


@app.route('/upload', methods=['POST'])
def upload():
    if 'disciplinas' in request.files:    
        file_out = request.files['disciplinas']
        data = file_out.read().decode('utf8')
        json_object = json.loads(data)

        with open('data/diciplinas.json', 'w') as file:
            json.dump(json_object, file)

    if 'docentes' in request.files:    
        file_out = request.files['docentes']
        data = file_out.read().decode('utf8')
        json_object = json.loads(data)

        with open('data/docentes.json', 'w') as file:
            json.dump(json_object, file)
    
    return "a"


@app.route('/optimize', methods=['POST'])
def optimize():
    with open('data/docentes.json', 'r') as file:
        docentes = json.load(file)

    with open('data/diciplinas.json', "r") as file:
        diciplinas = json.load(file)

    mydg.calcula(diciplinas, docentes)

    with open('data/resultado.json', "w") as file:
        json.dump(myam.array_object_to_dict(mydg.docentes), file)

    return 'Optimization'

@app.route('/show-results')
def show_results():
    return render_template('show_results.html')    


@app.route('/docentes-info')
def docentes_info():
    try:
        with open('data/resultado.json', 'r') as file:
            docentes = json.load(file)
        with open('data/diciplinas.json', 'r') as file:
            diciplinas = json.load(file)
    except:
        return "Arquivo diciplina e/ou o resultado da otimização não estão presentes"

    dic_obj = myam.dict_to_obj(diciplinas)
    dict_cod_turma = myam.dict_cod_turma(dic_obj)

    for doc in docentes:
        doc["disciplinas_dados"] = []
        for dis in doc["disciplinas"]:
            doc["disciplinas_dados"].append(dict_cod_turma[dis])

    return docentes



@app.route('/files-existence')
def files_existence():
    existencia = {"diciplinas": False, "docentes": False, "resultado": False}

    for ex in existencia:
        if os.path.exists("data/" + ex + ".json"):
            existencia[ex] = True



    return existencia

 
@app.route('/get-json/<caminho>')
def get_json(caminho):
    return caminho

if __name__ == '__main__':
    app.run(debug=True)