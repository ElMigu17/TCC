"""Nurse scheduling problem with shift requests."""
from ortools.sat.python import cp_model
from organizer.Estruturas_de_Dados import disciplina, docente, array_manipulator
import math

class distribuicao_graduacao:

    def __init__(self) -> None:
        self.fim_turno_manha = 11
        self.inicio_turno_noite = 17
        self.limite_inferior = 8
        self.limite_superior_padrao = 14
        self.limite_superior_reduzido = 12

        self.peso_infracao_horario = 0.5
        self.peso_desempate = 1

        self.restricao_horario_turnos = False
        self.restricao_horario_23_18 = False   

    def leitura_arquivo(self, name):
        am = array_manipulator()
        docentes = am.get_json(name)

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
    
## Restrições

    def res_um_doc_por_dis(self):
        for dis in self.disciplinas:
            self.modelo.AddExactlyOne(self.atribuicao[(doc.pos, dis.pos)] for doc in self.docentes)
            
    def res_limites_creditos(self):

        for doc in self.docentes:
            total = 0
            for dis in self.disciplinas:
                total += self.atribuicao[(doc.pos, dis.pos)]*dis.qtd_creditos

            self.modelo.Add(total >= self.limite_inferior)
            if doc.reducao == 1:
                self.modelo.Add(total <= self.limite_superior_reduzido)
            else: 
                self.modelo.Add(total <= self.limite_superior_padrao)

    def ha_conflito_horario(self, dis: disciplina, dis1: disciplina) -> bool:
        for aula in dis.horarios:
            for aula1 in dis1.horarios:
                aula_hi = self.hora_para_float(aula["hora_inicio"])
                aula1_hi = self.hora_para_float(aula1["hora_inicio"])
                aula_hf = self.hora_para_float(aula["hora_fim"])
                aula1_hf = self.hora_para_float(aula1["hora_fim"])

                if self.restricao_horario_23_18:
                    if (aula["dia_semana"] == aula1["dia_semana"]-1):
                        if ((aula_hi >= 21) and aula1_hi <= 10):
                            return  True

                    elif (aula1["dia_semana"] == aula["dia_semana"]-1):
                        if ((aula1_hi >= 21) and aula_hi <= 10):
                            return  True

                if((dis.pos != dis1.pos) and (aula["dia_semana"] == aula1["dia_semana"])):
                    if (((aula_hi <= aula1_hi) and (aula1_hi <= aula_hf))
                      or ((aula1_hi <= aula_hi) and (aula_hi <= aula1_hf))):
                        return  True
                    
                    elif(self.restricao_horario_turnos and
                      ((aula_hi <= self.fim_turno_manha and aula1_hi >= self.inicio_turno_noite) or 
                      (aula_hi >= self.inicio_turno_noite and aula1_hi <= self.fim_turno_manha))):
                        return  True
        return False

    def todos_conflitos_horario(self) -> list:
        ids_pares_proibidos = []
        for i in range(len(self.disciplinas)):
            for j in range(i, len(self.disciplinas)):
                dis = self.disciplinas

                if self.ha_conflito_horario(dis[i], dis[j]):
                    ids_pares_proibidos.append([dis[i].pos, dis[j].pos])
        return ids_pares_proibidos

    def res_horario(self):
        ids_pares_proibidos = self.todos_conflitos_horario()

        for doc in self.docentes:
            for par in ids_pares_proibidos:
                self.modelo.Add((self.atribuicao[(doc.pos, par[0])] + self.atribuicao[(doc.pos, par[1])]) <= 1)

    def res_prioridade(self):
        for doc in self.docentes:
            for pre in doc.preferencia:
                if pre in doc.disc_per_1 and not ( pre in doc.disc_per_2 and pre in doc.disc_per_3 ):
                    for dis in self.disciplinas:
                        if dis.string_cod_turma() == pre:
                            self.modelo.AddExactlyOne(self.atribuicao[(doc.pos, dis.pos)])

###Otimização

    def insere_ordenado(self, lista: list, doc: docente, cod_turma_dis: str):
        i = 0
        while(i < len(lista) and 
            lista[i].tem_mais_preferencia_que(doc, cod_turma_dis)):
            i += 1
        
        lista.insert(i, doc)
        
    def hankeia_por_disciplina(self):
        ranking = {}
        for dis in self.disciplinas:
            cod_turma_dis = dis.string_cod_turma()
            ranking[dis.pos] = []

            for doc in self.docentes:
                if cod_turma_dis in doc.preferencia:
                    self.insere_ordenado(ranking[dis.pos], doc, cod_turma_dis)
            
            if len(ranking[dis.pos]) <= 1:
                ranking.pop(dis.pos, None)
        
        return ranking    

    def opt_interesse(self):
        pref_disc = 0
        for doc in self.docentes:
            for dis in self.disciplinas:
                if dis.codigo in doc.preferencia:
                    pref_disc += (self.atribuicao[(doc.pos, dis.pos)] * doc.preferencia[dis.codigo])
        return pref_disc

    def opt_horarios(self):
        aux_restricao_horario_23_18 = not self.restricao_horario_23_18
        aux_restricao_horario_turnos = not self.restricao_horario_turnos
        self.restricao_horario_23_18 = True
        self.restricao_horario_turnos = True

        soma_peso = 0

        ids_pares_proibidos = self.todos_conflitos_horario()
        for doc in self.docentes:
            for par in ids_pares_proibidos:
                soma_peso += -(self.atribuicao[(doc.pos, par[0])] + self.atribuicao[(doc.pos, par[1])])*1

        self.restricao_horario_23_18 = aux_restricao_horario_23_18        
        self.restricao_horario_turnos = aux_restricao_horario_turnos

        return soma_peso

    def opt_desempate(self):
        self.ranking = self.hankeia_por_disciplina()

        opt_formula = 0
        for h in self.ranking:
            h_doc_list = self.ranking[h]
            tam = len(h_doc_list)

            for i in range(len(h_doc_list)):
                opt_formula += (self.atribuicao[(h_doc_list[i].pos, h)] * (tam-1))

        return opt_formula


# Exibições

    def exibe_solucao_achada(self, solver):
        qtd_preferencias = 0
        qtd_preferencias_peso = 0
        qtd_primeir_ranking_ganhador = 0
        array_creditos = []

        for doc in self.docentes:
            array_creditos.append(0)

            for dis in self.disciplinas:
                if solver.Value(self.atribuicao[(doc.pos, dis.pos)]) == 1:
                    add = ""
                    if dis.string_cod_turma() in doc.preferencia:
                        
                        add = "que possui preferencia " + str(doc.preferencia[dis.string_cod_turma()])
                        qtd_preferencias += 1
                        qtd_preferencias_peso += doc.preferencia[dis.string_cod_turma()]
                    
                    if dis.pos in self.ranking:
                        if doc == self.ranking[dis.pos][0]:
                            add += ", que era o primeiro no ranking"
                            qtd_primeir_ranking_ganhador += 1


                    print('Docente', doc.pos, 'lecionara a disciplina',  dis.pos, add)
                    array_creditos[-1] += dis.qtd_creditos
                    doc.disciplinas.append(dis.string_cod_turma())
            print("Quantidade total de creditos:", array_creditos[-1])

            print()
        print('Preferencias atendidas =', qtd_preferencias)
        print('Total de pesos de preferencia atendidos =', qtd_preferencias_peso)
        print('Quantidade de primeiros lugar no ranking ganhadores =', qtd_primeir_ranking_ganhador)
        media_creditos = sum(array_creditos)/len(self.docentes)
        print('Media de créditos: ', media_creditos)
        variancia = sum((a-media_creditos)*(a-media_creditos) for a in array_creditos)/(len(self.docentes)-1)
        print('Variancia de créditos: ', variancia)
        print('Desvio padrão de créditos: ', math.sqrt(variancia))

        am = array_manipulator()
        am.save_as_json(self.docentes, True)   

    def verifica_solucao(self):
        solver = cp_model.CpSolver()
        #solver.parameters.log_search_progress = True

        status = solver.Solve(self.modelo)

        if status == cp_model.OPTIMAL:
            print('Optimal solution:')

        elif status == cp_model.FEASIBLE:
            print('Feasible solution:')

        if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
            self.exibe_solucao_achada(solver)

        else:
            print('No solution found !')
            
        print('\nStatistics')
        print('  - conflicts: %i' % solver.NumConflicts())
        print('  - branches : %i' % solver.NumBranches())
        print('  - wall time: %f s' % solver.WallTime())
                
    def calcula(self, disciplinas, docentes):
        am = array_manipulator()
        
        self.disciplinas = am.dict_to_obj(disciplinas)
        self.docentes = am.dict_to_obj(docentes) 

        self.modelo = cp_model.CpModel()
        self.matriz_de_correlacao()      

        self.res_limites_creditos()
        self.res_um_doc_por_dis()
        self.res_horario()
        self.res_prioridade()
        
        soma_opt = self.opt_interesse()
        soma_opt += (self.opt_horarios() * self.peso_infracao_horario)
        soma_opt += (self.opt_desempate() * self.peso_desempate)

        self.modelo.Maximize(soma_opt)

        self.verifica_solucao()

def main():
    dg = distribuicao_graduacao()
    disciplinas = dg.leitura_arquivo("disciplina2022-2")
    docente = dg.leitura_arquivo("docente2022-2")
    dg.calcula(disciplinas, docente)

if __name__ == '__main__':
    main()
