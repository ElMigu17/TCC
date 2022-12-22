import pandas as pd
from Estruturas_de_Dados import disciplina, docente
import json
from datetime import date
import os

    
dia_num = {"Segunda-Feira" : 1,
    "Terça-Feira" : 2,
    "Quarta-Feira" : 3,
    "Quinta-Feira" : 4,
    "Sexta-Feira" : 5,
    "Sábado" : 6}

docentes = []
siape_docente = {}
disciplinas = []

def ano_semestre() -> str:
    hoje = date.today()
    semestre = int(hoje.month/7) + 1
    
    return str(hoje.year) + "-" + str(semestre)

def array_object_to_dict(array):
    my_dict = []
    for i in array:
        my_dict.append(i.__dict__)
    return my_dict

def save_as_json(array: list):
    nome_arquivo = "disciplina"
    if type(array[0]) == docente:
        nome_arquivo = "docente"
    nome_arquivo += ano_semestre()  
    path_saves = os.getcwd() + "/saves"
    out = array_object_to_dict(array)
    print("Salvando no arquivo: " + nome_arquivo)

    try:
        os.listdir(path_saves)
    except FileNotFoundError:
        os.mkdir(path_saves)

    with open(path_saves + "/" + nome_arquivo + ".json", "w") as outfile:
        json.dump(out, outfile)       

def importa_dados_disciplinas():

    Dados_Gerais = pd.read_excel('Modelos/Dados_Gerais.xlsx')
    prox_disciplina = {}
    id_i = 0

    def descobre_qtd_creditos(horarios):
        if(horarios[1].split(":")[1] == '50'):
            return 1
        else:
            return 2

    def cria_prox_disciplina(dado):
        prox_disciplina = {}
        horarios = dado['Horário'].split(' - ')
        prox_disciplina['horarios'] = [{ "dia_semana": dia_num[dado['Dia']], "hora_inicio": horarios[0], "hora_fim": horarios[1]}]
        prox_disciplina['disciplina'] = dado['Disciplina']
        prox_disciplina['turmas'] = [dado['Turma']]
        prox_disciplina['qtd_creditos'] = descobre_qtd_creditos(horarios)

        return prox_disciplina


    for i in Dados_Gerais.index:
        dado = Dados_Gerais.loc[i]
        if pd.isna(dado['Disciplina']):
            if not dado['Turma'] in prox_disciplina['turmas']:
                prox_disciplina['turmas'].append(dado['Turma'])

        else:
            if not bool(prox_disciplina):
                prox_disciplina = cria_prox_disciplina(dado)
                continue

            if ((dado['Disciplina'] != prox_disciplina['disciplina']) 
              or (not dado['Turma'] in prox_disciplina['turmas'])):

                disciplinas.append( disciplina( id_i, prox_disciplina['disciplina'], 
                    prox_disciplina['qtd_creditos'],
                    prox_disciplina['horarios'], 
                    True, 
                    prox_disciplina['turmas']))
                id_i += 1

                prox_disciplina = cria_prox_disciplina(dado)
            else:
                horarios = dado['Horário'].split(' - ')
                prox_disciplina['horarios'].append({ "dia_semana": dia_num[dado['Dia']], "hora_inicio": horarios[0], "hora_fim": horarios[1]})          
                prox_disciplina['qtd_creditos'] += descobre_qtd_creditos(horarios)

def importa_dados_profs():
    doscentes_dados = pd.read_excel('Modelos/Doscentes.xlsx')
    index = 0

    for i in doscentes_dados.index:
        docentes.append(docente(index, doscentes_dados.iloc[i]['Nome'], int(doscentes_dados.iloc[i]['SIAPE'])))
        siape_docente[doscentes_dados.iloc[i]['SIAPE']] = index
        index += 1 

def row_ou_zero(row):
    try:
        return int(row)
    except:
        return 0

def importa_dados_passados():
    Semestres_passados = pd.ExcelFile('Modelos/Semestres_anteriores.xlsx')
    anterior = Semestres_passados.parse('anterior')

    for i in anterior.index:

        row = anterior.iloc[i]
        if i == 0:
            continue
        
        num_disc = row_ou_zero(row["Número de Disciplinas"])
        num_estudantes = row_ou_zero(row["nº estudantes fim de período"])
        creditos = row_ou_zero(row["Créditos"])

        docentes[siape_docente[i]].add_info_ultimo_periodo(num_disc, num_estudantes, creditos)

def importa_preferencias():
    Preferencias = pd.read_excel('Modelos/Preferencias.xlsx', index_col=0)
    qtd_profs = int(Preferencias.size/Preferencias.index.size)

    for i in range(1, qtd_profs+1):
        for j in Preferencias.index:
            if not pd.isna(Preferencias[i][j]):
                print(int(Preferencias[i][j]), j)
                docentes[siape_docente[i]].add_preferencia(int(Preferencias[i][j]), j)


def main():
    
    importa_dados_profs()
    importa_dados_passados()
    importa_dados_disciplinas()
    importa_preferencias()
    save_as_json(disciplinas)
    save_as_json(docentes)

if __name__ == '__main__':
    main()