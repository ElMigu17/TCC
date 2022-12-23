"""Nurse scheduling problem with shift requests."""
from ortools.sat.python import cp_model
from Estruturas_de_Dados import disciplina, docente, array_manipulator

class distribuicao_graduacao:

    def __init__(self) -> None:
        self.fim_turno_manha = 11
        self.inicio_turno_noite = 17
        pass

    # def leitura_disciplinas(self):
    #     disciplinas = [
    #         disciplina(0, 'GMM101', 2, [{ "dia_semana": 3, "hora_inicio": "13:00", "hora_fim": "14:40"}], True, ['9A']),
    #         disciplina(1, 'GMM101', 4, [{ "dia_semana": 5, "hora_inicio": "19:00", "hora_fim": "20:40"}], True, ['26A']),
    #         disciplina(2, 'GMM101', 4, [{ "dia_semana": 4, "hora_inicio": "13:00", "hora_fim": "14:40"}, { "dia_semana": 5, "hora_inicio": "13:00", "hora_fim": "14:40"}], True, ['13A', '10A', '21A']),
    #         disciplina(3, 'GMM101', 2, [{ "dia_semana": 2, "hora_inicio": "8:00", "hora_fim": "9:40"}, { "dia_semana": 5, "hora_inicio": "15:00", "hora_fim": "16:40"}], True, ['30C', '30A']),
    #         disciplina(4, 'GMM101', 6,
    #         [{ "dia_semana": 1, "hora_inicio": "13:00", "hora_fim": "9:40"}, { "dia_semana": 3, "hora_inicio": "15:00", "hora_fim": "16:40"}, { "dia_semana": 5, "hora_inicio": "19:00", "hora_fim": "20:40"}],
    #         True, ['30G', '30E'])
    #     ]

    #     return disciplinas

    # def leitura_docentes(self):
    #     docentes = [
    #         docente(0, "claudin", 123456),
    #         docente(1, "roger", 654321)
    #     ]

    #     return docentes

    def leitura_disciplinas(self):
        am = array_manipulator()
        disciplinas = am.get_json("disciplina2022-2")

        return disciplinas

    def leitura_docentes(self):
        am = array_manipulator()
        docentes = am.get_json("docente2022-2")
        return docentes
        
    def hora_para_float(self, hor: str):
        split_hor = hor.split(":")

        split_hor[0] = float(split_hor[0])
        split_hor[1] = float(split_hor[1])

        split_hor[0] += split_hor[1]/100
        return split_hor[0]
    
    def principal(self):
        self.distribui_disciplinas_com_prioridade()
        self.distribui_restante()

    def matriz_de_correlacao(self) -> dict:
        assignment = {}
        for doc in self.docentes:
            for dis in self.disciplinas:
                assignment[(doc.pos, dis.pos)] = self.model.NewBoolVar('assignment_doc%idis%i' % (doc.pos, dis.pos)) 
        return assignment

    def res_um_doc_por_dis(self, assignment):
        for dis in self.disciplinas:
            self.model.AddExactlyOne(assignment[(doc.pos, dis.pos)] for doc in self.docentes)
            
    def res_limites_creditos(self, assignment):
        for doc in self.docentes:
            total = 0
            for dis in self.disciplinas:
                total += assignment[(doc.pos, dis.pos)]*dis.qtd_creditos
            self.model.Add(total >= 8)
            self.model.Add(total <= 16)

    def ha_conflito_horario(self, dis: disciplina, dis1: disciplina) -> bool:
        for aula in dis.horarios:
            for aula1 in dis1.horarios:
                aula_hi = self.hora_para_float(aula["hora_inicio"])
                aula1_hi = self.hora_para_float(aula1["hora_inicio"])
                aula_hf = self.hora_para_float(aula["hora_fim"])
                aula1_hf = self.hora_para_float(aula1["hora_fim"])

                if (aula["dia_semana"] == aula1["dia_semana"]-1):
                    if ((aula_hi >= 21) and aula1_hi <= 10):
                        return  True

                elif (aula1["dia_semana"] == aula["dia_semana"]-1):
                    if ((aula1_hi >= 21) and aula_hi <= 10):
                        return  True

                if ((dis.pos != dis1.pos) and (aula["dia_semana"] == aula1["dia_semana"])):
                    if (((aula_hi <= aula1_hi) and (aula1_hi <= aula_hf))
                      or ((aula1_hi <= aula_hi) and (aula_hi <= aula1_hf))):
                        return  True
                    
                    elif ((aula_hi <= self.fim_turno_manha and aula1_hi >= self.inicio_turno_noite) or 
                          (aula_hi >= self.inicio_turno_noite and aula1_hi <= self.fim_turno_manha)):
                        return  True
        return False

    def res_horario(self, assignment: dir):
        
        ids_pares_proibidos = []
        for i in range(len(self.disciplinas)):
            for j in range(i, len(self.disciplinas)):
                dis = self.disciplinas
                if self.ha_conflito_horario(dis[i], dis[j]):
                    ids_pares_proibidos.append([dis[i].pos, dis[j].pos])

        for doc in self.docentes:
            for par in ids_pares_proibidos:
                self.model.Add((assignment[(doc.pos, par[0])] + assignment[(doc.pos, par[1])]) <= 1)
                


        
    def calcula(self):
        self.disciplinas = self.leitura_disciplinas()
        self.docentes = self.leitura_docentes()
        self.model = cp_model.CpModel()
        assignment = self.matriz_de_correlacao()      

        self.res_um_doc_por_dis(assignment)
        self.res_limites_creditos(assignment)
        self.res_horario(assignment)

        solver = cp_model.CpSolver()
        status = solver.Solve(self.model)


        if status == cp_model.OPTIMAL:
            print('Optimal solution:')
            for doc in self.docentes:
                for dis in self.disciplinas:
                    if solver.Value(assignment[(doc.pos, dis.pos)]) == 1:
                        print('Professor', doc.pos, 'lecionara a disciplina',  dis.pos)
                        doc.discplinas.append(dis.pos)
                print()
            print(f'Number of shift requests met = {solver.ObjectiveValue()}')

        elif status == cp_model.FEASIBLE:
            print('Feasible solution:')
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

        am = array_manipulator()
        am.save_as_json(self.docentes, True)


def main():
    dg = distribuicao_graduacao()
    dg.calcula()

if __name__ == '__main__':
    main()
