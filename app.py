from flask import Flask, request, render_template, send_file
import json
from solver.Modelo import distribuicao_graduacao
from solver.Estruturas_de_Dados import array_manipulator
from solver.LerCsv import leitor_csv
import sass
import os

app = Flask(__name__)
arr_man = array_manipulator()

PREFERENCIAS_HEAD_CSV = 'Peso,1,2,3,4,5'
DOSCENTES_HEAD_CSV = 'SIAPE,Nome,Redução'
DISCIPLINAS_HEAD_CSV = 'Disciplina,Local,Tipo,Tempo,Período,Dia,Horário,Turma,Vagas Normais,Vagas Reservadas para Calouros,Vagas para Matrícula Especial,Total Vagas Normais,Total Vagas Reservadas para Calouros,Total Vagas para Matrícula Especial,Docente,'
QTD_FIM_ULTIMO_SEMESTRE = 'SIAPE,Professores,Créditos,Número de Disciplinas,nº estudantes fim de período'

ARQ_DISCIPLINA = 'data/disciplinas.json'
ARQ_DOCENTE = 'data/docentes.json'
ARQ_SOLUCAO = 'data/solucao.json'
ARQ_DADO_SOLUCAO = 'data/dados_solucao.json'

NOME_ARQUIVO_HEAD_CSV = {
    'docentes_csv': DOSCENTES_HEAD_CSV,
    'disciplinas_prox': DISCIPLINAS_HEAD_CSV,
    'qtd_fim_ultimo_semestre': QTD_FIM_ULTIMO_SEMESTRE,
    'preferencias': PREFERENCIAS_HEAD_CSV,
    'ultimo_semestre': DISCIPLINAS_HEAD_CSV,
    'penultimo_semestre': DISCIPLINAS_HEAD_CSV,
    'antipenultimo_semestre': DISCIPLINAS_HEAD_CSV
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
        for key in NOME_ARQUIVO_HEAD_CSV:
            arquivos_com_erro.append('\n' + str(i) + ' - ' + enviar_file(request, key, 'csv'))
            i += 1
    else:
        arquivos_com_erro.append('\n1 - ' + enviar_file(request, 'disciplinas', 'json'))
        arquivos_com_erro.append('\n2 - ' + enviar_file(request, 'docentes', 'json'))
        
    arquivos_com_erro = (a for a in arquivos_com_erro if 'null' not in a)
    return arquivos_com_erro

@app.route('/enviar_um_arquivo/<tipo_arquivo>', methods=['POST'])
def enviar_um_arquivo(tipo_arquivo):
    filename = [a for a in request.files.keys()]
    a = enviar_file(request, filename[0], tipo_arquivo)

    if a == 'null':
        a = []
    return a

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
            if data.split('\n')[0] == NOME_ARQUIVO_HEAD_CSV[file_name]:
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
        try:
            leitor.main('data/docentes_csv.csv', 
                    'data/disciplinas_prox.csv', 
                    'data/qtd_fim_ultimo_semestre.csv',
                    'data/preferencias.csv',
                    'data/ultimo_semestre.csv',
                    'data/penultimo_semestre.csv', 
                    'data/antipenultimo_semestre.csv'
                    )
        except ValueError as e:
            erro_str = ''
            for er in e.args:
                erro_str += er
            return {'erro': erro_str}
        
        retorno = leitor.docentes_not_found
        
        am = array_manipulator()
        docentes = am.array_object_to_dict(leitor.docentes)
        with open(ARQ_DOCENTE, 'w') as file:
            json.dump(docentes, file)


        disciplinas = am.array_object_to_dict(leitor.disciplinas)
        with open(ARQ_DISCIPLINA, 'w') as file:
            json.dump(disciplinas, file)

    with open(ARQ_DOCENTE, 'r') as file:
        docentes = json.load(file)

    with open(ARQ_DISCIPLINA, 'r') as file:
        disciplinas = json.load(file)

    dados_solucao = dist_grad.main(disciplinas, docentes)

    if dados_solucao:
        with open(ARQ_SOLUCAO, 'w') as file:
            json.dump(arr_man.array_object_to_dict(dist_grad.docentes), file)
        with open(ARQ_DADO_SOLUCAO, 'w') as file:
            json.dump(dados_solucao, file)
    else:
        return 'No solution found'
    return retorno

@app.route('/docentes-info')
def docentes_info():
    try:
        with open(ARQ_SOLUCAO, 'r') as file:
            docentes = json.load(file)
        with open(ARQ_DADO_SOLUCAO, 'r') as file:
            dados_solucao = json.load(file)
        with open(ARQ_DISCIPLINA, 'r') as file:
            disciplinas = json.load(file)
    except:
        return 'Arquivo de disciplina e/ou o solucao da otimização não estão presentes'

    dic_obj = arr_man.dict_to_obj(disciplinas)
    dict_cod_turma = arr_man.dict_cod_turma(dic_obj)

    for doc in docentes:
        doc['disciplinas_dados'] = []
        for dis in doc['disciplinas']:
            doc['disciplinas_dados'].append(dict_cod_turma[dis])

    return {'docentes': docentes, 'dados_solucao': dados_solucao}

@app.route('/erros-de-leitura')
def erros_de_leitura():
    try:
        with open('data/erros.json', 'r') as file:
            incoerencias = json.load(file)
    except:
        return 'Arquivo de erros não está presentes'

    return {'incoerencias': incoerencias}

@app.route('/files-existence/<tipo_arquivo>')
def files_existence(tipo_arquivo):
    existencia = {'disciplinas': False, 'docentes': False}
    if tipo_arquivo == 'csv':
        existencia = {'docentes_csv': False, 
                      'disciplinas_prox': False,
                      'qtd_fim_ultimo_semestre': False, 
                      'preferencias': False,
                      'ultimo_semestre': False, 
                      'penultimo_semestre': False,
                      'antipenultimo_semestre': False}
        
    for ex in existencia:
        existencia[ex] = os.path.exists('data/' + ex + '.' + tipo_arquivo)

    existencia['solucao'] = os.path.exists(ARQ_SOLUCAO)

    return existencia

@app.route('/download/<tipo_arquivo>')
def download_file(tipo_arquivo):
    if not os.path.exists(ARQ_SOLUCAO):
        return 'Arquivo de otimização não encontrado'
    
    if tipo_arquivo == 'csv':
        converte_solucao_csv()

    PATH='data/solucao.' + tipo_arquivo
    return send_file(PATH,as_attachment=True, download_name=('distribuicao_prox_semestre.' + tipo_arquivo))

def converter_scss():
    sass.compile(dirname=('static/sass', 'static/css'), output_style='compressed')

def converte_solucao_csv():
    with open(ARQ_SOLUCAO, 'r') as file:
        solucao_json = json.load(file)
    with open('data/disciplinas_prox.csv', 'r') as file:
        dados_gerais = file.read()
    dados_output = ''
    novos_dados = dados_gerais.split('\n')
    dados_output = novos_dados.pop(0) + '\n'
    dados_gerais = list(map(lambda d: d.split(','),novos_dados))

    def find_doc(cod_turma):
        i = 0
        while i < len(solucao_json):
            if cod_turma in solucao_json[i]['disciplinas']:
                return solucao_json[i]['nome']
            i += 1
        raise ValueError('Não foi encontrado professor que ministra a disciplina ' + cod_turma)

    for i in range(len(dados_gerais)):
        dado = dados_gerais[i]

        if dado[0] == '':
            dados_output += novos_dados[i] + '\n'
            continue
        codigo_turma = dado[0] + '_' 
        turmas = [dado[7]]

        j = i+1
        while len(dados_gerais[j]) > 1 and dados_gerais[j][0] == '':
            turmas.append(dados_gerais[j][7])
            j += 1
        turmas.sort()
        codigo_turma += ''.join(turmas)

        prof = find_doc(codigo_turma)
        dado[14] = prof

        for d in dado:
            dados_output += d + ','
        dados_output = dados_output[:-1]
        dados_output += '\n'

    with open('data/solucao.csv', 'w') as file:
        file.write(dados_output)


@app.route('/validar_solucao/', methods=['POST'])
def validar_solucao():
    pares_restricao = []
    for par in request.json['pares_restricao']:
        pares_restricao.append((par[0], par[1]))
    
    retorno = 'Optimization'
    dist_grad = distribuicao_graduacao()

    with open(ARQ_DOCENTE, 'r') as file:
        docentes = json.load(file)

    with open(ARQ_DISCIPLINA, 'r') as file:
        disciplinas = json.load(file)

    dados_solucao = dist_grad.valida(disciplinas, docentes, pares_restricao)

    if dados_solucao:
        with open(ARQ_SOLUCAO, 'w') as file:
            json.dump(arr_man.array_object_to_dict(dist_grad.docentes), file)
        with open(ARQ_DADO_SOLUCAO, 'w') as file:
            json.dump(dados_solucao, file)
    else:
        return 'No solution found'
    return retorno


if __name__ == '__main__':
    app.run(debug=True)



#https://sass.github.io/libsass-python/index.html