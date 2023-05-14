from solver.Estruturas_de_Dados import disciplina, docente, array_manipulator

class leitor_csv:
    def __init__(self) -> None:
        self.dia_num = {"Seg" : 1,
            "Ter" : 2,
            "Qua" : 3,
            "Qui" : 4,
            "Sex" : 5,
            "Sáb" : 6,
            "Sab" : 6}

        self.docentes = []
        self.siape_docente = {}
        self.disciplinas = []
        self.docentes_not_found = {}

    def cria_prox_disciplina(self, Dados_Gerais, i):
        def descobre_qtd_creditos(horarios):
            if(horarios[1].split(":")[1] == '50'):
                return 1
            elif(horarios[1].split(":")[1] == '40'):
                return 2
            else:
                return 3

        dado = Dados_Gerais[i]
        try:
            dia_semana = self.get_pos_weekday([dado[5]])
        except Exception as e:
            raise ValueError(e.args[0] + "na linha " + str(i))  
        
        aux_disciplina = {}
        horarios = dado[6].split(' - ')
        aux_disciplina['horarios'] = [{ "dia_semana": dia_semana, "hora_inicio": horarios[0], "hora_fim": horarios[1]}]
        aux_disciplina['disciplina'] = dado[0]
        aux_disciplina['turmas'] = [dado[7]]
        aux_disciplina['docente'] = dado[14]
        aux_disciplina['qtd_creditos'] = descobre_qtd_creditos(horarios)
        i += 1
        while i < len(Dados_Gerais) and len(Dados_Gerais[i]) >2 and Dados_Gerais[i][0] == '':
            aux_disciplina['turmas'].append(Dados_Gerais[i][7])
            i += 1

        return aux_disciplina, i

    def get_pos_weekday(self, this_dia):
        for d in self.dia_num:
            if d in this_dia[0]:
                return self.dia_num[d]
        raise ValueError("Erro na nomeação do dia da semana")
    
    def num_ou_zero(self, num):
        try:
            return int(num)
        except:
            return 0

    def importa_dados_disciplinas(self, caminho_arquivo):
        Dados_Gerais = ""
        with open(caminho_arquivo, 'r') as file:
            Dados_Gerais = file.read()
        Dados_Gerais = Dados_Gerais.split("\n")
        Dados_Gerais = list(map(lambda d: d.split(","),Dados_Gerais))
        if not Dados_Gerais[0][0].isdigit():
            Dados_Gerais.pop(0)

        aux_disciplina = {}
        id_i = 0
        
        prox_disciplina, index = self.cria_prox_disciplina(Dados_Gerais, 0)
        while len(Dados_Gerais) > index and len(Dados_Gerais[index]) > 2:
            aux_disciplina, index = self.cria_prox_disciplina(Dados_Gerais, index)
            if(aux_disciplina["disciplina"] == prox_disciplina["disciplina"] and 
               aux_disciplina["turmas"] == prox_disciplina["turmas"]):

                prox_disciplina["horarios"].append(aux_disciplina["horarios"][0])
                prox_disciplina['qtd_creditos'] += aux_disciplina['qtd_creditos']
                aux_disciplina = {}
            
            else:
                self.disciplinas.append( disciplina( id_i, prox_disciplina['disciplina'], 
                    prox_disciplina['qtd_creditos'],
                    prox_disciplina['horarios'], 
                    True, 
                    prox_disciplina['turmas']))
                prox_disciplina = aux_disciplina
                aux_disciplina = {}
                id_i += 1


        self.disciplinas.append( disciplina( id_i, prox_disciplina['disciplina'], 
            prox_disciplina['qtd_creditos'],
            prox_disciplina['horarios'], 
            True, 
            prox_disciplina['turmas']))

    def disciplinas_lecionadas_anteriormente(self, caminho_arquivo, semestre):
        Dados_Gerais = ""
        self.docentes_not_found[semestre] = []
        with open(caminho_arquivo, 'r') as file:
            Dados_Gerais = file.read()
        Dados_Gerais = Dados_Gerais.split("\n")
        Dados_Gerais = list(map(lambda d: d.split(","),Dados_Gerais))
        if not Dados_Gerais[0][0].isdigit():
            Dados_Gerais.pop(0)

        aux_disciplina = {}
        id_i = 0      
        index = 0

        def tenta_add_turma_a_docente(prox_disciplina):

            docente_alvo = None
            i = 0
            str_disc_turma = prox_disciplina['disciplina'] + "_"

            for it in prox_disciplina['turmas']:
                str_disc_turma += it

            while i < len(self.docentes):
                if prox_disciplina["docente"] in self.docentes[i].nome:
                    if docente_alvo != None:
                        
                        aux = getattr( self.docentes[docente_alvo], semestre)
                        aux.pop()
                        setattr( self.docentes[docente_alvo], semestre, aux)

                        i = len(self.docentes)
                        docente_alvo = None
                    else:
                        docente_alvo = i
                        
                        aux = getattr( self.docentes[i], semestre)
                        aux.append(str_disc_turma)
                        setattr( self.docentes[i], semestre, aux)
                        
                i+=1

            if docente_alvo == None:
                self.docentes_not_found[semestre].append(str_disc_turma)
            

        
        prox_disciplina, index = self.cria_prox_disciplina(Dados_Gerais, 0)
        while len(Dados_Gerais) > index and len(Dados_Gerais[index]) > 2:
            aux_disciplina, index = self.cria_prox_disciplina(Dados_Gerais, index)
            if(aux_disciplina["disciplina"] == prox_disciplina["disciplina"] and 
               aux_disciplina["turmas"] == prox_disciplina["turmas"]):
                aux_disciplina = {}
                continue
            
            else:
                tenta_add_turma_a_docente(prox_disciplina)
                prox_disciplina = aux_disciplina
                aux_disciplina = {}
                id_i += 1
        print(self.disciplinas)
        tenta_add_turma_a_docente(prox_disciplina)



    def importa_dados_profs(self, caminho_arquivo):
        doscentes_dados = ""
        with open(caminho_arquivo, 'r') as file:
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
            self.docentes.append(docente(index, dosc_dados[1], int(dosc_dados[0]), reducao))
            self.siape_docente[dosc_dados[0]] = index
            index += 1 

    def importa_quantidades_passado(self, caminho_arquivo):
        ultimo_semestre = ""

        with open(caminho_arquivo, 'r') as file:
            ultimo_semestre = file.read()
        
        index = 0
        ultimo_semestre = ultimo_semestre.split("\n")
        ultimo_semestre = list(map(lambda d: d.split(","),ultimo_semestre))
        if not ultimo_semestre[0][0].isdigit():
            ultimo_semestre.pop(0)
            
        while len(ultimo_semestre) > index and ultimo_semestre[index][0].isdigit():
            row = ultimo_semestre[index]

            num_disc = self.num_ou_zero(row[3])
            num_estudantes = self.num_ou_zero(row[4])
            creditos = self.num_ou_zero(row[2])
            siape = row[0]
            
            self.docentes[self.siape_docente[siape]].add_info_ultimo_periodo(num_disc, num_estudantes, creditos)

            index += 1
        
    def importa_preferencias(self, caminho_arquivo):
        Preferencias = ""

        with open(caminho_arquivo, 'r') as file:
            Preferencias = file.read()
        Preferencias = Preferencias.split("\n")
        Preferencias = list(map(lambda d: d.split(","),Preferencias))
        peso = Preferencias.pop(0)
        peso.pop(0)
        i = 0
        while len(Preferencias[i]) > 2 and len(Preferencias) > i:
            j = 1
            pos_docente_atual = self.siape_docente[Preferencias[i][0]]
            while len(Preferencias[i]) > j:
                self.docentes[pos_docente_atual].add_preferencia(j, Preferencias[i][j])
                j += 1
            i += 1

    def main(self, 
             dados_profs,
             dados_disciplinas, 
             dados_passado, 
             preferencias, 
             ultimo_semestre, 
             penultimo_semestre, 
             antipenultimo_semestre):
        funcoes = [ 
            self.importa_dados_profs, 
            self.importa_dados_disciplinas,
            self.importa_quantidades_passado,
            self.importa_preferencias,
            self.disciplinas_lecionadas_anteriormente,
            self.disciplinas_lecionadas_anteriormente,
            self.disciplinas_lecionadas_anteriormente
        ]
        parametros =[
            (dados_profs),
            (dados_disciplinas),
            (dados_passado),
            (preferencias),
            (ultimo_semestre, 'disc_per_1'),
            (penultimo_semestre, 'disc_per_2'),
            (antipenultimo_semestre, 'disc_per_3')
        ]

        for i in range(len(funcoes)):
            try:
                if len(parametros[i]) == 2:
                    funcoes[i](parametros[i][0], parametros[i][1])
                else:
                    funcoes[i](parametros[i])
            except ValueError as e:
                raise ValueError( e.args[0] + " \nNa função: "+ funcoes[i].__name__ + " \nCom parametros: " + parametros[i])
            except Exception as e:
                raise Exception(e)



if __name__ == '__main__':
    leitor = leitor_csv()
    leitor.main("Modelos/Doscentes.csv", "Modelos/2022-2.csv", "Modelos/Dados_Gerais.csv", "Modelos/Preferencias2.0.csv")