import pandas as pd
from Estruturas_de_Dados import disciplina, docente, array_manipulator
    
dia_num = {"Segunda-Feira" : 1,
    "Terça-Feira" : 2,
    "Quarta-Feira" : 3,
    "Quinta-Feira" : 4,
    "Sexta-Feira" : 5,
    "Sábado" : 6}

docentes = []
siape_docente = {}
disciplinas = []
disc_me_importa = []

def importa_dados_disciplinas():

    Dados_Gerais = pd.read_excel('Dados2022-2.xlsx')
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

        prox_disciplina['disciplina'] = dado['Disciplina']
        prox_disciplina['turmas'] = [dado['Turma']]
        prox_disciplina['qtd_creditos'] = descobre_qtd_creditos(horarios)
        prox_disciplina['docente'] = dado['Docente']

        return prox_disciplina
    
    def disc_turma_string(disciplina):
        turmas = disciplina['turmas']
        turmas.sort()
        turmas_as_string = ""
        for turma in turmas:
            turmas_as_string += turma
        return disciplina['disciplina'] + "_" + turmas_as_string


    for i in Dados_Gerais.index:
        dado = Dados_Gerais.loc[i]
        if pd.isna(dado['Disciplina']):
            if not dado['Turma'] in prox_disciplina['turmas']:
                prox_disciplina['turmas'].append(dado['Turma'])

        else:
            if dado['Disciplina'] == "PMA 504":
                break
            if not bool(prox_disciplina):
                prox_disciplina = cria_prox_disciplina(dado)
                continue

            if ((dado['Disciplina'] != prox_disciplina['disciplina']) 
              or (not dado['Turma'] in prox_disciplina['turmas'])):
                
                disc_me_importa.append({"prof": prox_disciplina['docente'],
                    "dis": disc_turma_string(prox_disciplina), 
                    "qtd_creditos": prox_disciplina['qtd_creditos']})
                id_i += 1

                prox_disciplina = cria_prox_disciplina(dado)



def main():
    
    importa_dados_disciplinas()
    res = sorted(disc_me_importa, key = lambda k: k['prof'])
    por_prof = [{"prof": 'lixo', "dis": "lixo"}]
    for dis in res:
        if por_prof[-1]["prof"] == dis["prof"]:
            por_prof[-1]['dis'].append(dis["dis"])
        else:
            por_prof.append({"prof": dis["prof"], "dis": [dis["dis"]]})
    print(por_prof)
    for dis in por_prof:
        print(dis["prof"])
        print(dis["dis"])
        print()


if __name__ == '__main__':
    main()