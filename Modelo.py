"""Nurse scheduling problem with shift requests."""
from ortools.sat.python import cp_model
from Estruturas_de_Dados import disciplina, docente, array_manipulator
import math

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
        self.atribuicao = {}
        for doc in self.docentes:
            for dis in self.disciplinas:
                self.atribuicao[(doc.pos, dis.pos)] = self.modelo.NewBoolVar('atribuicao_doc%idis%i' % (doc.pos, dis.pos)) 
    

    def res_um_doc_por_dis(self):
        for dis in self.disciplinas:
            self.modelo.AddExactlyOne(self.atribuicao[(doc.pos, dis.pos)] for doc in self.docentes)
            
    def res_limites_creditos(self):
        total_creditos = sum(dis.qtd_creditos for dis in self.disciplinas)
        media_creditos = int(total_creditos/len(self.docentes))
        print(media_creditos)
        squares = []
        for doc in self.docentes:
            total = 0
            for dis in self.disciplinas:
                total += self.atribuicao[(doc.pos, dis.pos)]*dis.qtd_creditos
            if doc.reducao == 1:
                self.modelo.Add(total >= 5)
                self.modelo.Add(total <= 13)
            else: 
                self.modelo.Add(total >= 8)
                self.modelo.Add(total <= 16)
                aux = media_creditos-total
                squares.append(self.modelo.NewIntVar(-(16**2), (16**2), f'diff_doc{doc.pos}'))
                self.modelo.AddMultiplicationEquality(squares[-1], [aux, aux])

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

    def res_horario(self):
        
        ids_pares_proibidos = []
        for i in range(len(self.disciplinas)):
            for j in range(i, len(self.disciplinas)):
                dis = self.disciplinas
                if self.ha_conflito_horario(dis[i], dis[j]):
                    ids_pares_proibidos.append([dis[i].pos, dis[j].pos])

        for doc in self.docentes:
            for par in ids_pares_proibidos:
                self.modelo.Add((self.atribuicao[(doc.pos, par[0])] + self.atribuicao[(doc.pos, par[1])]) <= 1)
                
    def res_preferencia(self):
        for doc in self.docentes:
            for pre in doc.preferencia:
                if pre in doc.disc_per_1 and not ( pre in doc.disc_per_2 and pre in doc.disc_per_3 ):
                    aux = 0
                    for dis in self.disciplinas:
                        aux += self.atribuicao[(doc.pos, dis.pos)]
                    self.modelo.Add(aux >= doc.disc_per_1.count(pre))


    def opt_interesse(self):

        for doc in self.docentes:
            pref_disc = 0
            for dis in self.disciplinas:
                if dis.codigo in doc.preferencia:
                    pref_disc += (self.atribuicao[(doc.pos, dis.pos)] * doc.preferencia[dis.codigo])
            self.modelo.Maximize(pref_disc)

        
    def calcula(self):
        self.disciplinas = self.leitura_disciplinas()
        self.docentes = self.leitura_docentes()
        self.modelo = cp_model.CpModel()
        self.matriz_de_correlacao()      

        self.res_limites_creditos()
        print(self.modelo)
        self.res_um_doc_por_dis()
        self.res_horario()
        self.res_preferencia()
        self.opt_interesse()


        solver = cp_model.CpSolver()
        #solver.parameters.log_search_progress = True
        status = solver.Solve(self.modelo)


        if status == cp_model.OPTIMAL:
            print('Optimal solution:')
        elif status == cp_model.FEASIBLE:
            print('Feasible solution:')

        if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
            qtd_preferencias = 0
            qtd_preferencias_peso = 0
            array_creditos = []

            for doc in self.docentes:
                array_creditos.append(0)

                for dis in self.disciplinas:
                    if solver.Value(self.atribuicao[(doc.pos, dis.pos)]) == 1:
                        add = ""
                        if dis.codigo in doc.preferencia:
                            add = "que possui preferencia " + str(doc.preferencia[dis.codigo])
                            qtd_preferencias += 1
                            qtd_preferencias_peso += doc.preferencia[dis.codigo]
                        print('Docente', doc.pos, 'lecionara a disciplina',  dis.pos, add)
                        array_creditos[-1] += dis.qtd_creditos
                        doc.discplinas.append(dis.pos)
                print("Quantidade total de creditos:", array_creditos[-1])

                print()
            print('Quantidade de preferencias atendidas =', qtd_preferencias, qtd_preferencias_peso)
            media_creditos = sum(array_creditos)/len(self.docentes)
            print('Media de créditos: ', media_creditos)
            variancia = sum((a-media_creditos)*(a-media_creditos) for a in array_creditos)/(len(self.docentes)-1)
            print('Variancia de créditos: ', variancia)
            print('Media padrão de créditos: ', math.sqrt(variancia))
            
        else:
            print('No solution found !')
            #print(solver.SolutionInfo())
            
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
