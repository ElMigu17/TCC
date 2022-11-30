"""Nurse scheduling problem with shift requests."""
from ortools.sat.python import cp_model

class disciplina:
    def __init__(self, id, qtd_creditos: int, nome: str, codigo: str, horarios: list, eh_graduacao: bool, turmas: list) -> None:
        self.id = id
        self.qtd_creditos = qtd_creditos
        self.nome = nome
        self.codigo = codigo
        self.docente = None
        self.horarios = horarios
        self.eh_graduacao = eh_graduacao
        self.turmas = turmas
    


class docente:
    def __init__(self, num_id, nome: str, id: int) -> None:
        self.num_id = num_id
        self.nome = nome
        self.id = id
        self.discplinas = []
        self.disc_per_1 = []  #disciplina periodo -1
        self.disc_per_2 = []
        self.disc_per_3 = []
    
    def discplinas_com_preferencia(self):
        #TODO
        return None

    def nao_ha_conflito(self, horarios_nova_disciplina: list):
        for d in self.disciplinas:
            for h_doc in d.horarios:
                for h_nov in horarios_nova_disciplina:
                    if h_doc["dia_semana"] == h_nov["dia_semana"]:
                        if (h_doc["hora_inicio"] == h_nov["hora_inicio"]
                        or h_doc["hora_inicio"]+1 == h_nov["hora_inicio"]
                        or h_doc["hora_inicio"]-1 == h_nov["hora_inicio"]):

                            return False
        return True
class distribuicao_graduacao:

    def __init__(self) -> None:
        pass

    def leitura_disciplinas(self):
        disciplinas = [
            disciplina(0, 2, 'teste', 'GMM101', [{ "dia_semana": 2, "hora_inicio": 13}], True, ['9A']),
            disciplina(1, 4, 'teste', 'GMM101', [{ "dia_semana": 5, "hora_inicio": 19}], True, ['26A']),
            disciplina(2, 4, 'teste', 'GMM102', [{ "dia_semana": 4, "hora_inicio": 13}, { "dia_semana": 5, "hora_inicio": 10}], True, ['13A', '10A', '21A']),
            disciplina(3, 2, 'teste', 'GMM102', [{ "dia_semana": 3, "hora_inicio": 13}, { "dia_semana": 5, "hora_inicio": 15}], True, ['30C', '30A']),
            disciplina(4, 6, 'teste', 'GMM104',
            [{ "dia_semana": 1, "hora_inicio": 13}, { "dia_semana": 3, "hora_inicio": 15}, { "dia_semana": 5, "hora_inicio": 17}],
            True, ['30G', '30E'])
        ]

        return disciplinas

    def leitura_docentes(self):
        docentes = [
            docente(0, "claudin", 123456),
            docente(1, "roger", 654321)
        ]

        return docentes
        
    def principal(self):
        self.distribui_disciplinas_com_prioridade()
        self.distribui_restante()

    def matriz_de_correlacao(self):
        assignment = {}
        for doc in self.docentes:
            for dis in self.disciplinas:
                assignment[(doc.num_id, dis.id)] = self.model.NewBoolVar('assignment_doc%idis%i' % (doc.num_id, dis.id)) 
                print(type(assignment[(doc.num_id, dis.id)]))
        return assignment

    def res_um_doc_por_dis(self, assignment):
        for dis in self.disciplinas:
            self.model.AddExactlyOne(assignment[(doc.num_id, dis.id)] for doc in self.docentes)

    def res_min_oito_creditos(self, assignment):
        for doc in self.docentes:
            total = 0
            for dis in self.disciplinas:
                total += assignment[(doc.num_id, dis.id)]*dis.qtd_creditos
            self.model.Add(total >= 8)

    def res_horario_21_10(self, assignment: dir):
        
        ids_pares_proibidos = []
        for dis in self.disciplinas:
            for dis1 in self.disciplinas:
                par = self.res_horario_21_10_aula(dis, dis1)
                if par != None:
                    ids_pares_proibidos.append(par)

        for doc in self.docentes:
            pares_proibidos = 0
            for par in ids_pares_proibidos:
                pares_proibidos += ((assignment[(doc.num_id, par[0])] * 1) + (assignment[(doc.num_id, par[1])] * 1))
            self.model.Add(pares_proibidos == 0)

    def res_horario_21_10_aula(self, dis: disciplina, dis1: disciplina):
        for aula in dis.horarios:
            for aula1 in dis1.horarios:

                if (aula["dia_semana"] == aula1["dia_semana"]-1):
                    if (aula["hora_inicio"] == 21 and aula1["hora_inicio"] <= 10):
                        return  [dis.id, dis1.id]

                elif ((dis.id != dis1.id) and (aula["dia_semana"] == aula1["dia_semana"])):

                    if ((aula["hora_inicio"] == aula1["hora_inicio"]) or (aula["hora_inicio"] == aula1["hora_inicio"]+1) or (aula["hora_inicio"] == aula1["hora_inicio"]-1)):
                        return  [dis.id, dis1.id]
                    
                    elif ((aula["hora_inicio"] < 11 and aula1["hora_inicio"] > 17) or 
                          (aula["hora_inicio"] > 17 and aula1["hora_inicio"] < 11)):
                        return  [dis.id, dis1.id]
        return None
        
    def calcula(self):
        self.disciplinas = self.leitura_disciplinas()
        self.docentes = self.leitura_docentes()
        self.model = cp_model.CpModel()
        assignment = self.matriz_de_correlacao()      

        self.res_um_doc_por_dis(assignment)
        self.res_min_oito_creditos(assignment)
        self.res_horario_21_10(assignment)

        solver = cp_model.CpSolver()
        status = solver.Solve(self.model)


        if status == cp_model.OPTIMAL:
            print('Solution:')
            for doc in self.docentes:
                for dis in self.disciplinas:
                    if solver.Value(assignment[(doc.num_id, dis.id)]) == 1:
                        print('Professor', doc.num_id, 'lecionara a disciplina',  dis.id)
                print()
            print(f'Number of shift requests met = {solver.ObjectiveValue()}')
        else:
            print('No optimal solution found !')
            
        # Statistics.
        print('\nStatistics')
        print('  - conflicts: %i' % solver.NumConflicts())
        print('  - branches : %i' % solver.NumBranches())
        print('  - wall time: %f s' % solver.WallTime())




def main():
    dg = distribuicao_graduacao()
    dg.calcula()

if __name__ == '__main__':
    main()
