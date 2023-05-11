from flask import Flask, request, render_template, send_file
import json
from solver.Modelo import distribuicao_graduacao
from solver.Estruturas_de_Dados import array_manipulator
from solver.LerCsv import leitor_csv
import sass
import os

app = Flask(__name__)
arr_man = array_manipulator()

preferencia_head_csv = "Peso,1,2,3,4,5"
doscentes_head_csv = "SIAPE,Nome,Redução"
disciplinas_head_csv = "Disciplina,Local,Tipo,Tempo,Período,Dia,Horário,Turma,Vagas Normais,Vagas Reservadas para Calouros,Vagas para Matrícula Especial,Total Vagas Normais,Total Vagas Reservadas para Calouros,Total Vagas para Matrícula Especial,Docente,"
qtd_fim_ultimo_semestre = "SIAPE,Professores ,Créditos,Número de Disciplinas,nº estudantes fim de período"

nome_arquivo_head_csv = {
    'docentes_csv': doscentes_head_csv,
    'disciplinas_prox': disciplinas_head_csv,
    'qtd_fim_ultimo_semestre': qtd_fim_ultimo_semestre,
    'preferencias': preferencia_head_csv,
    'ultimo_semestre': disciplinas_head_csv,
    'penultimo_semestre': disciplinas_head_csv,
    'antipenultimo_semestre': disciplinas_head_csv
}

item_arquivo_json = {
    'disciplinas': 'codigo',
    'docentes': 'nome'
}

@app.route('/', methods=['GET'])
def index():
    converter_scss()
    return render_template('index.html')

@app.route('/enviar/<tipo_arquivo>', methods=['POST'])
def enviar(tipo_arquivo):
    arquivos_com_erro = []
    if tipo_arquivo == 'csv':
        i = 1
        for key in nome_arquivo_head_csv:
            arquivos_com_erro.append('\n' + str(i) + ' - ' + enviar_file(request, key, 'csv'))
            # arquivos_com_erro.append('\n2 - ' + enviar_file(request, 'disciplinas_prox', 'csv'))
            # arquivos_com_erro.append('\n3 - ' + enviar_file(request, 'preferencias', 'csv'))
            # arquivos_com_erro.append('\n3 - ' + enviar_file(request, 'preferencias', 'csv'))'qtd_fim_ultimo_semestre'
            # arquivos_com_erro.append('\n4 - ' + enviar_file(request, 'ultimo_semestre', 'csv'))
            # arquivos_com_erro.append('\n5 - ' + enviar_file(request, 'penultimo_semestre', 'csv'))
            # arquivos_com_erro.append('\n6 - ' + enviar_file(request, 'antipenultimo_semestre', 'csv'))
            i += 1
    else:
        arquivos_com_erro.append('\n1 - ' + enviar_file(request, 'disciplinas', 'json'))
        arquivos_com_erro.append('\n2 - ' + enviar_file(request, 'docentes', 'json'))
        
    arquivos_com_erro = (a for a in arquivos_com_erro if 'null' not in a)
    return arquivos_com_erro

def enviar_file(request, file_name, tipo_arquivo):
    if file_name in request.files:
        file_out = request.files[file_name]
        data = file_out.read().decode('utf8')

        if data == '':
            return 'null'
        
        if tipo_arquivo == 'json':
            json_object = json.loads(data)

            if item_arquivo_json[file_name] in json_object[0]:
                with open('data/' + file_name + '.json', 'w') as file:
                    json.dump(json_object, file)
                return 'null'
        else:
            if data.split("\n")[0] == nome_arquivo_head_csv[file_name]:
                with open('data/' + file_name + '.csv', 'w') as file:
                    file.write(data)
                return 'null'
        return file_name
    return 'null'

@app.route('/solver/<tipo_arquivo>', methods=['POST'])
def solver(tipo_arquivo):
    retorno = 'Optimization'
    dist_grad = distribuicao_graduacao()
    if tipo_arquivo == 'csv':
        leitor = leitor_csv()
        leitor.main("data/docentes_csv.csv", 
                    "data/disciplinas_prox.csv", 
                    "data/qtd_fim_ultimo_semestre.csv",
                    "data/preferencias.csv",
                    "data/ultimo_semestre.csv",
                    "data/penultimo_semestre.csv", 
                    "data/antipenultimo_semestre.csv"
                    )
        
        retorno = leitor.docentes_not_found
        
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

    dados_solucao = dist_grad.main(disciplinas, docentes)

    if dados_solucao:
        with open('data/solucao.json', "w") as file:
            json.dump(arr_man.array_object_to_dict(dist_grad.docentes), file)
        with open('data/dados_solucao.json', "w") as file:
            json.dump(dados_solucao, file)
    else:
        return 'No solution found'
    return retorno

@app.route('/docentes-info')
def docentes_info():
    try:
        with open('data/solucao.json', 'r') as file:
            docentes = json.load(file)
        with open('data/dados_solucao.json', 'r') as file:
            dados_solucao = json.load(file)
        with open('data/disciplinas.json', 'r') as file:
            disciplinas = json.load(file)
    except:
        return "Arquivo de disciplina e/ou o solucao da otimização não estão presentes"

    dic_obj = arr_man.dict_to_obj(disciplinas)
    dict_cod_turma = arr_man.dict_cod_turma(dic_obj)

    for doc in docentes:
        doc["disciplinas_dados"] = []
        for dis in doc["disciplinas"]:
            doc["disciplinas_dados"].append(dict_cod_turma[dis])

    return {"docentes": docentes, "dados_solucao": dados_solucao}

@app.route('/files-existence/<tipo_arquivo>')
def files_existence(tipo_arquivo):
    existencia = {"disciplinas": False, "docentes": False}
    if tipo_arquivo == 'csv':
        existencia = {"docentes_csv": False, 
                      "disciplinas_prox": False,
                      "qtd_fim_ultimo_semestre": False, 
                      "preferencias": False,
                      "ultimo_semestre": False, 
                      "penultimo_semestre": False,
                      "antipenultimo_semestre": False}
        
    for ex in existencia:
        existencia[ex] = os.path.exists("data/" + ex + "." + tipo_arquivo)

    existencia["solucao"] = os.path.exists("data/solucao.json")

    return existencia

@app.route('/download/<tipo_arquivo>')
def Download_File(tipo_arquivo):
    if not os.path.exists("data/solucao.json"):
        return "Arquivo de otimização não encontrado"
    
    if tipo_arquivo == "csv":
        converte_solucao_csv()

    PATH='data/solucao.' + tipo_arquivo
    return send_file(PATH,as_attachment=True, download_name=("distribuicao_prox_semestre." + tipo_arquivo))

def converter_scss():
    sass.compile(dirname=('static/sass', 'static/css'), output_style='compressed')

def converte_solucao_csv():
    with open("data/solucao.json", 'r') as file:
        solucao_json = json.load(file)
    with open("data/disciplinas_prox.csv", 'r') as file:
        Dados_Gerais = file.read()
    dados_output = ""
    novos_dados = Dados_Gerais
    novos_dados = Dados_Gerais.split("\n")
    dados_output = novos_dados.pop(0) + "\n"
    Dados_Gerais = list(map(lambda d: d.split(","),novos_dados))

    def find_doc(cod_turma):
        i = 0
        while i < len(solucao_json):
            if cod_turma in solucao_json[i]["disciplinas"]:
                return solucao_json[i]["nome"]
            i += 1
        raise ValueError("Não foi encontrado professor que ministra essa disciplina")

    for i in range(len(Dados_Gerais)):
        dado = Dados_Gerais[i]

        if dado[0] == '':
            dados_output += novos_dados[i] + "\n"
            continue
        codigo_turma = dado[0] + "_" 
        turmas = [dado[7]]

        j = i+1
        while len(Dados_Gerais[j]) > 1 and Dados_Gerais[j][0] == '':
            turmas.append(Dados_Gerais[j][7])
            j += 1
        turmas.sort()
        codigo_turma += ''.join(turmas)

        prof = find_doc(codigo_turma)
        dado[14] = prof

        for d in dado:
            dados_output += d + ","
        dados_output = dados_output[:-1]
        dados_output += "\n"

    with open('data/solucao.csv', 'w') as file:
        file.write(dados_output)

if __name__ == '__main__':
    app.run(debug=True)



#https://sass.github.io/libsass-python/index.html