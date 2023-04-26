from flask import Flask, request, render_template
import json
from organizer.Modelo import distribuicao_graduacao
from organizer.Estruturas_de_Dados import array_manipulator
import sass
import os

app = Flask(__name__)
dist_grad = distribuicao_graduacao()
arr_man = array_manipulator()


@app.route('/', methods=['GET'])
def index():
    converte_scss()
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

    dist_grad.calcula(diciplinas, docentes)

    with open('data/resultado.json', "w") as file:
        json.dump(arr_man.array_object_to_dict(dist_grad.docentes), file)

    return 'Optimization'

@app.route('/docentes-info')
def docentes_info():
    try:
        with open('data/resultado.json', 'r') as file:
            docentes = json.load(file)
        with open('data/diciplinas.json', 'r') as file:
            diciplinas = json.load(file)
    except:
        return "Arquivo diciplina e/ou o resultado da otimização não estão presentes"

    dic_obj = arr_man.dict_to_obj(diciplinas)
    dict_cod_turma = arr_man.dict_cod_turma(dic_obj)

    for doc in docentes:
        doc["disciplinas_dados"] = []
        for dis in doc["disciplinas"]:
            doc["disciplinas_dados"].append(dict_cod_turma[dis])

    return docentes

@app.route('/files-existence')
def files_existence():
    existencia = {"diciplinas": False, "docentes": False, "resultado": False}

    for ex in existencia:
        existencia[ex] = os.path.exists("data/" + ex + ".json")

    return existencia

def converte_scss():
    sass.compile(dirname=('static/sass', 'static/css'), output_style='compressed')


if __name__ == '__main__':
    app.run(debug=True)



#https://sass.github.io/libsass-python/index.html