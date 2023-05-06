from solver.Estruturas_de_Dados import disciplina, docente, array_manipulator

class leitor_csv:
    def __init__(self) -> None:
        self.dia_num = {"Segunda-Feira" : 1,
            "Terça-Feira" : 2,
            "Quarta-Feira" : 3,
            "Quinta-Feira" : 4,
            "Sexta-Feira" : 5,
            "Sábado" : 6}

        self.docentes = []
        self.siape_docente = {}
        self.disciplinas = []
    
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

        def descobre_qtd_creditos(horarios):
            if(horarios[1].split(":")[1] == '50'):
                return 1
            else:
                return 2
            
        def cria_prox_disciplina(i):
            dado = Dados_Gerais[i]
            aux_disciplina = {}
            horarios = dado[6].split(' - ')
            aux_disciplina['horarios'] = [{ "dia_semana": self.dia_num[dado[5]], "hora_inicio": horarios[0], "hora_fim": horarios[1]}]
            aux_disciplina['disciplina'] = dado[0]
            aux_disciplina['turmas'] = [dado[7]]
            aux_disciplina['qtd_creditos'] = descobre_qtd_creditos(horarios)
            i += 1
            while i < len(Dados_Gerais) and len(Dados_Gerais[i]) >2 and Dados_Gerais[i][0] == '':
                aux_disciplina['turmas'].append(Dados_Gerais[i][7])
                i += 1

            return aux_disciplina, i
        
        prox_disciplina, index = cria_prox_disciplina(0)
        while len(Dados_Gerais) > index and len(Dados_Gerais[index]) > 2:
            aux_disciplina, index = cria_prox_disciplina(index)
            print(aux_disciplina["disciplina"])
            print(aux_disciplina["turmas"] == prox_disciplina["turmas"],aux_disciplina["turmas"], prox_disciplina["turmas"])
            if(aux_disciplina["disciplina"] == prox_disciplina["disciplina"] and 
               aux_disciplina["turmas"] == prox_disciplina["turmas"]):
                print("aaaaaaaaaaaa")

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

    def importa_dados_passados(self, caminho_arquivo):
        ultimo_semestre = ""

        with open(caminho_arquivo, 'r') as file:
            ultimo_semestre = file.read()
        
        index = 0
        ultimo_semestre = ultimo_semestre.split("\n")
        ultimo_semestre = list(map(lambda d: d.split(","),ultimo_semestre))
        if not ultimo_semestre[0][0].isdigit():
            ultimo_semestre.pop(0)
            
        while ultimo_semestre[index][0].isdigit() and len(ultimo_semestre) > index:
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

    def main(self, dados_profs, dados_passado, dados_disciplinas, preferencias):
        self.importa_dados_profs(dados_profs)
        self.importa_dados_passados(dados_passado)
        self.importa_dados_disciplinas(dados_disciplinas)
        self.importa_preferencias(preferencias)
        am = array_manipulator()
        am.save_as_json(self.disciplinas)
        am.save_as_json(self.docentes)


if __name__ == '__main__':
    leitor = leitor_csv()
    leitor.main("Modelos/Doscentes.csv", "Modelos/2022-2.csv", "Modelos/Dados_Gerais.csv", "Modelos/Preferencias2.0.csv")