from flask import Flask, request, render_template
import json
from organizer.Modelo import distribuicao_graduacao
from organizer.Estruturas_de_Dados import array_manipulator
from organizer.LerCsv import leitor_csv
import sass
import os

app = Flask(__name__)
dist_grad = distribuicao_graduacao()
arr_man = array_manipulator()


@app.route('/', methods=['GET'])
def index():
    converte_scss()
    return render_template('upload.html')

@app.route('/upload/<file_type>', methods=['POST'])
def upload(file_type):
    if file_type == 'csv':
        upload_file(request, 'docentes_csv', 'csv')
        upload_file(request, 'ultimo_semestre', 'csv')
        upload_file(request, 'disciplinas_prox', 'csv')
        upload_file(request, 'preferencias', 'csv')
    else:
        upload_file(request, 'disciplinas', 'json')
        upload_file(request, 'docentes', 'json')
   
    return "a"

def upload_file(request, file_name, file_type):
    if file_name in request.files:
        file_out = request.files[file_name]
        data = file_out.read().decode('utf8')

        if file_type == 'json':
            json_object = json.loads(data)
            with open('data/' + file_name + '.json', 'w') as file:
                json.dump(json_object, file)

        else:
            if data != '':
                with open('data/' + file_name + '.csv', 'w') as file:
                    file.write(data)

@app.route('/optimize/<file_type>', methods=['POST'])
def optimize(file_type):
    if file_type == 'csv':
        leitor = leitor_csv()
        leitor.main("data/docentes_csv.csv", "data/ultimo_semestre.csv", "data/disciplinas_prox.csv", "data/preferencias.csv")
        
        am = array_manipulator()
        docentes = am.array_object_to_dict(leitor.docentes)
        with open('data/docentes.json', 'w') as file:
            json.dump(docentes, file)


        disciplinas = am.array_object_to_dict(leitor.disciplinas)
        with open('data/disciplinas.json', 'w') as file:
            json.dump(disciplinas, file)

    with open('data/docentes.json', 'r') as file:
        docentes = json.load(file)

    with open('data/disciplinas.json', "r") as file:
        disciplinas = json.load(file)

    dist_grad.calcula(disciplinas, docentes)

    with open('data/resultado.json', "w") as file:
        json.dump(arr_man.array_object_to_dict(dist_grad.docentes), file)

    return 'Optimization'

@app.route('/docentes-info')
def docentes_info():
    try:
        with open('data/resultado.json', 'r') as file:
            docentes = json.load(file)
        with open('data/disciplinas.json', 'r') as file:
            disciplinas = json.load(file)
    except:
        return "Arquivo disciplina e/ou o resultado da otimização não estão presentes"

    dic_obj = arr_man.dict_to_obj(disciplinas)
    dict_cod_turma = arr_man.dict_cod_turma(dic_obj)

    for doc in docentes:
        doc["disciplinas_dados"] = []
        for dis in doc["disciplinas"]:
            doc["disciplinas_dados"].append(dict_cod_turma[dis])

    return docentes

@app.route('/files-existence/<file_type>')
def files_existence(file_type):
    existencia = {"disciplinas": False, "docentes": False}
    if file_type == 'csv':
        existencia = {"docentes_csv": False, 
                      "ultimo_semestre": False, 
                      "disciplinas_prox": False,
                      "preferencias": False}

    for ex in existencia:
        existencia[ex] = os.path.exists("data/" + ex + "." + file_type)

    existencia["resultado"] = os.path.exists("data/resultado.json")

    return existencia

def converte_scss():
    sass.compile(dirname=('static/sass', 'static/css'), output_style='compressed')


if __name__ == '__main__':
    app.run(debug=True)



#https://sass.github.io/libsass-python/index.html