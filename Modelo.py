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
            disciplina(0, 2, 'teste', 'GMM101', [{ "dia_semana": 2, "hora_inicio": 15}], True, ['9A']),
            disciplina(1, 2, 'teste', 'GMM101', [{ "dia_semana": 5, "hora_inicio": 19}], True, ['26A']),
            disciplina(2, 4, 'teste', 'GMM102', [{ "dia_semana": 4, "hora_inicio": 9}, { "dia_semana": 5, "hora_inicio": 7}], True, ['13A', '10A', '21A']),
            disciplina(3, 4, 'teste', 'GMM102', [{ "dia_semana": 2, "hora_inicio": 7}, { "dia_semana": 5, "hora_inicio": 7}], True, ['30C', '30A']),
            disciplina(4, 6, 'teste', 'GMM104', [{ "dia_semana": 1, "hora_inicio": 8}, { "dia_semana": 3, "hora_inicio": 8}, { "dia_semana": 5, "hora_inicio": 8}], True, ['30G', '30E'])
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
        assignemt = {}
        for doc in self.docentes:
            for dis in self.disciplinas:
                assignemt[(doc.num_id, dis.id)] = self.model.NewBoolVar('assignemt_doc%idis%i' % (doc.num_id, dis.id)) 
        return assignemt

    def res_um_doc_por_dis(self, assignemt):
        for dis in self.disciplinas:
            self.model.AddExactlyOne(assignemt[(doc.num_id, dis.id)] for doc in self.docentes)

    def res_min_oito_creditos(self, assignemt):
        for doc in self.docentes:
            total = 0
            for dis in self.disciplinas:
                total += assignemt[(doc.num_id, dis.id)]*dis.qtd_creditos
            self.model.Add(total >= 8)

    def calcula(self):
        self.disciplinas = self.leitura_disciplinas()
        self.docentes = self.leitura_docentes()
        self.model = cp_model.CpModel()
        assignemt = self.matriz_de_correlacao()      

        self.res_um_doc_por_dis(assignemt)
        self.res_min_oito_creditos(assignemt)

        solver = cp_model.CpSolver()
        status = solver.Solve(self.model)

        print(self.model)

        if status == cp_model.OPTIMAL:
            print('Solution:')
            for doc in self.docentes:
                for dis in self.disciplinas:
                    if solver.Value(assignemt[(doc.num_id, dis.id)]) == 1:
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
