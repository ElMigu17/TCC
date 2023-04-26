from Estruturas_de_Dados import disciplina, docente, array_manipulator
import csv

dia_num = {"Segunda-Feira" : 1,
    "Terça-Feira" : 2,
    "Quarta-Feira" : 3,
    "Quinta-Feira" : 4,
    "Sexta-Feira" : 5,
    "Sábado" : 6}

docentes = []
siape_docente = {}
disciplinas = []

def importa_dados_disciplinas():
    Dados_Gerais = ""
    with open('Modelos/Dados_Gerais.csv', 'r') as file:
        Dados_Gerais = file.read()
    Dados_Gerais = Dados_Gerais.split("\n")
    Dados_Gerais = list(map(lambda d: d.split(","),Dados_Gerais))
    if not Dados_Gerais[0][0].isdigit():
        Dados_Gerais.pop(0)

    prox_disciplina = {}
    id_i = 0
    index = 0

    def descobre_qtd_creditos(horarios):
        if(horarios[1].split(":")[1] == '50'):
            return 1
        else:
            return 2
        
    def cria_prox_disciplina(dado):
        prox_disciplina = {}
        horarios = dado[6].split(' - ')
        prox_disciplina['horarios'] = [{ "dia_semana": dia_num[dado[5]], "hora_inicio": horarios[0], "hora_fim": horarios[1]}]
        prox_disciplina['disciplina'] = dado[0]
        prox_disciplina['turmas'] = [dado[7]]
        prox_disciplina['qtd_creditos'] = descobre_qtd_creditos(horarios)

        return prox_disciplina
    while len(Dados_Gerais[index]) > 2 and len(Dados_Gerais) > index:
        dado = Dados_Gerais[index]
        if dado[0] == '':
            if not dado[7] in prox_disciplina['turmas']:
                prox_disciplina['turmas'].append(dado[7])

        else:
            if not bool(prox_disciplina):
                prox_disciplina = cria_prox_disciplina(dado)
                continue

            if ((dado[0] != prox_disciplina['disciplina']) 
              or (not dado[7] in prox_disciplina['turmas'])):

                disciplinas.append( disciplina( id_i, prox_disciplina['disciplina'], 
                    prox_disciplina['qtd_creditos'],
                    prox_disciplina['horarios'], 
                    True, 
                    prox_disciplina['turmas']))
                id_i += 1

                prox_disciplina = cria_prox_disciplina(dado)
            else:
                horarios = dado[6].split(' - ')
                prox_disciplina['horarios'].append({ "dia_semana": dia_num[dado[5]], "hora_inicio": horarios[0], "hora_fim": horarios[1]})          
                prox_disciplina['qtd_creditos'] += descobre_qtd_creditos(horarios)
        index += 1

def importa_dados_profs():
    doscentes_dados = ""
    with open('Modelos/Doscentes.csv', 'r') as file:
        doscentes_dados = file.read()

    index = 0
    doscentes_dados = doscentes_dados.split("\n")
    doscentes_dados = list(map(lambda d: d.split(","),doscentes_dados))
    if not doscentes_dados[0][0].isdigit():
        doscentes_dados.pop(0)
        
    while doscentes_dados[index][0].isdigit() and len(doscentes_dados) > index:
        dosc_dados = doscentes_dados[index]
        reducao = 0

        if not dosc_dados[2].isdigit():
            reducao = int(dosc_dados[2].isdigit())
        docentes.append(docente(index, dosc_dados[1], int(dosc_dados[0]), reducao))
        siape_docente[dosc_dados[0]] = index
        index += 1 

def num_ou_zero(num):
    try:
        return int(num)
    except:
        return 0

def importa_dados_passados():
    ultimo_semestre = ""

    with open('Modelos/2022-2.csv', 'r') as file:
        ultimo_semestre = file.read()
    
    index = 0
    ultimo_semestre = ultimo_semestre.split("\n")
    ultimo_semestre = list(map(lambda d: d.split(","),ultimo_semestre))
    if not ultimo_semestre[0][0].isdigit():
        ultimo_semestre.pop(0)
        
    while ultimo_semestre[index][0].isdigit() and len(ultimo_semestre) > index:
        row = ultimo_semestre[index]

        num_disc = num_ou_zero(row[3])
        num_estudantes = num_ou_zero(row[4])
        creditos = num_ou_zero(row[2])
        siape = row[0]
        
        docentes[siape_docente[siape]].add_info_ultimo_periodo(num_disc, num_estudantes, creditos)

        index += 1
    

def importa_preferencias():
    Preferencias = ""

    with open('Modelos/Preferencias.csv', 'r') as file:
        Preferencias = file.read()
    Preferencias = Preferencias.split("\n")
    Preferencias = list(map(lambda d: d.split(","),Preferencias))
    siape_docentes_preferencia = Preferencias.pop(0)
    siape_docentes_preferencia.pop(0)
   
    i = 0
    while len(Preferencias[i]) > 2 and len(Preferencias) > i:
        j = 1
        while len(Preferencias[i]) > j:
            if Preferencias[i][j].isdigit():
                siape_atual = siape_docente[siape_docentes_preferencia[j-1]]
                docentes[siape_atual].add_preferencia(int(Preferencias[i][j]), j)
            j += 1
        i += 1


def main():
    
    importa_dados_profs()
    importa_dados_passados()
    importa_dados_disciplinas()
    importa_preferencias()
    am = array_manipulator()
    am.save_as_json(disciplinas)
    am.save_as_json(docentes)

if __name__ == '__main__':
    main()