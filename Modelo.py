"""Nurse scheduling problem with shift requests."""
from ortools.sat.python import cp_model
from Estruturas_de_Dados import disciplina, docente

class distribuicao_graduacao:

    def __init__(self) -> None:
        self.fim_turno_manha = 11
        self.inicio_turno_noite = 17
        pass

    def leitura_disciplinas(self):
        disciplinas = [
            disciplina(0, 'GMM101', 2, [{ "dia_semana": 2, "hora_inicio": 13}], True, ['9A']),
            disciplina(1, 'GMM101', 4, [{ "dia_semana": 5, "hora_inicio": 19}], True, ['26A']),
            disciplina(2, 'GMM101', 4, [{ "dia_semana": 4, "hora_inicio": 13}, { "dia_semana": 5, "hora_inicio": 13}], True, ['13A', '10A', '21A']),
            disciplina(3, 'GMM101', 2, [{ "dia_semana": 3, "hora_inicio": 13}, { "dia_semana": 5, "hora_inicio": 15}], True, ['30C', '30A']),
            disciplina(4, 'GMM101', 6,
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
                assignment[(doc.pos, dis.pos)] = self.model.NewBoolVar('assignment_doc%idis%i' % (doc.pos, dis.pos)) 
                print(type(assignment[(doc.pos, dis.pos)]))
        return assignment

    def res_um_doc_por_dis(self, assignment):
        for dis in self.disciplinas:
            self.model.AddExactlyOne(assignment[(doc.pos, dis.pos)] for doc in self.docentes)

    def res_min_oito_creditos(self, assignment):
        for doc in self.docentes:
            total = 0
            for dis in self.disciplinas:
                total += assignment[(doc.pos, dis.pos)]*dis.qtd_creditos
            self.model.Add(total >= 8)

    def aux_res_horario(self, dis: disciplina, dis1: disciplina):
        for aula in dis.horarios:
            for aula1 in dis1.horarios:

                if (aula["dia_semana"] == aula1["dia_semana"]-1):
                    if ((aula["hora_inicio"] >= 21) and aula1["hora_inicio"] <= 10):
                        return  [dis.pos, dis1.pos]

                elif (aula1["dia_semana"] == aula["dia_semana"]-1):
                    if ((aula1["hora_inicio"] >= 21) and aula["hora_inicio"] <= 10):
                        return  [dis.pos, dis1.pos]

                elif ((dis.pos != dis1.pos) and (aula["dia_semana"] == aula1["dia_semana"])):

                    if ((aula["hora_inicio"] == aula1["hora_inicio"]) 
                      or (aula["hora_inicio"] == aula1["hora_inicio"]+1) 
                      or (aula["hora_inicio"] == aula1["hora_inicio"]-1)):
                        return  [dis.pos, dis1.pos]
                    
                    elif ((aula["hora_inicio"] <= self.fim_turno_manha and aula1["hora_inicio"] >= self.inicio_turno_noite) or 
                          (aula["hora_inicio"] >= self.inicio_turno_noite and aula1["hora_inicio"] <= self.fim_turno_manha)):
                        return  [dis.pos, dis1.pos]
        return None

    def res_horario(self, assignment: dir):
        
        ids_pares_proibidos = []
        for dis in self.disciplinas:
            for dis1 in self.disciplinas:
                par = self.aux_res_horario(dis, dis1)
                if par != None:
                    ids_pares_proibidos.append(par)

        for doc in self.docentes:
            pares_proibidos = 0
            for par in ids_pares_proibidos:
                pares_proibidos += ((assignment[(doc.pos, par[0])] * 1) + (assignment[(doc.pos, par[1])] * 1))
            self.model.Add(pares_proibidos == 0)


        
    def calcula(self):
        self.disciplinas = self.leitura_disciplinas()
        self.docentes = self.leitura_docentes()
        self.model = cp_model.CpModel()
        assignment = self.matriz_de_correlacao()      

        self.res_um_doc_por_dis(assignment)
        self.res_min_oito_creditos(assignment)
        self.res_horario(assignment)

        solver = cp_model.CpSolver()
        status = solver.Solve(self.model)


        if status == cp_model.OPTIMAL:
            print('Solution:')
            for doc in self.docentes:
                for dis in self.disciplinas:
                    if solver.Value(assignment[(doc.pos, dis.pos)]) == 1:
                        print('Professor', doc.pos, 'lecionara a disciplina',  dis.pos)
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
