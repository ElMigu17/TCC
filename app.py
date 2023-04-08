from flask import Flask, request, render_template, jsonify
import json
from organizer.Modelo import distribuicao_graduacao as dg
from organizer.Estruturas_de_Dados import array_manipulator as am

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

        with open('saves/diciplinas.json', 'w') as file:
            json.dump(json_object, file)

    if 'docentes' in request.files:    
        file_out = request.files['docentes']
        data = file_out.read().decode('utf8')
        json_object = json.loads(data)

        with open('saves/docentes.json', 'w') as file:
            json.dump(json_object, file)
    
    return "a"


@app.route('/optimize', methods=['POST'])
def optimize():
    print("aaaaaaaaaaaaaaaaa")
    with open('saves/docentes.json', 'r') as file:
        docentes = json.load(file)

    with open('saves/diciplinas.json', "r") as file:
        diciplinas = json.load(file)


    print(type(diciplinas))
    mydg.calcula(diciplinas)

    # Do something with the data...
    return 'File uploaded successfully!'


@app.route('/show-results')
def show_results():
    return render_template('show_results.html')    


@app.route('/disciplinas-info')
def disciplinas_info():
    dictionary = mydg.leitura_arquivo("disciplina2022-2")
    a = myam.dict_cod_turma(dictionary)
    return a
 
@app.route('/get-json/<caminho>')
def get_json(caminho):
    return caminho

if __name__ == '__main__':
    app.run(debug=True)