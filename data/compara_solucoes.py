import json

# with open('comhorario_semprioridade.json', 'r') as file:
#     comhorario = json.load(file)
# with open('semhorario_comprioridade.json', 'r') as file:
#     semhorario = json.load(file)


# qtd_total = 0
# qtd_certo = 0
# for i in range(len(comhorario)):
#     print(comhorario[i]['disciplinas'])
#     print(semhorario[i]['disciplinas'])
#     print('--------------------------------------------------------------')
#     for d in comhorario[i]['disciplinas']:
#         qtd_total += 1
#         if d in semhorario[i]['disciplinas']:
#             qtd_certo += 1

# print("+++++++++++++++++++++++++++++++++++++++++++")


# for doc in comhorario:
#     note = []
#     for pre in doc['preferencia']:
#         if pre in doc['disc_per_1'] and not ( pre in doc['disc_per_2'] and pre in doc['disc_per_3'] ):
#             note.append(pre)
    
#     for n in note:
#         if n in doc['disciplinas']:
#             print("aaaaaaaaaaaaaaaaaaaaaaaa")
#     print(note)   

# print(qtd_total)
# print(qtd_certo)


rankings = {
    "GMM101_26A": ['Daiane Alice Henrique Ament', 'Helvécio Geovani Fargnoli Filho'] ,
    "GMM101_9A": ['Daiane Alice Henrique Ament', 'Helvécio Geovani Fargnoli Filho'] ,
    "GMM102_30E30G": ['Marcio Fialho Chaves', 'Nelson Antonio Silva'] ,
    "GMM102_3A5A": ['Eliza Maria Ferreira', 'Nelson Antonio Silva'] ,
    "GMM104_3A5A": ['Andreia da Silva Coutinho', 'Gustavo Cipolat Colvero', 'Ana Carolina Dias do Amaral Ramos', 'Adriana Xavier Freitas'] ,
    "GMM104_19A": ['Andreia da Silva Coutinho', 'Adriana Xavier Freitas'] ,
    "GMM104_30A30C": ['Andreia da Silva Coutinho', 'Gustavo Cipolat Colvero'] ,
    "GMM106_15A18A": ['Andreza Cristina Beezão Moreira', 'Fernando Lourenço', 'Graziane Sales Teodoro'] ,
    "GMM106_30A30B": ['Andreza Cristina Beezão Moreira', 'Gustavo Cipolat Colvero', 'Jose Alves Oliveira'] ,
    "GMM108_22A3A": ['Fernando Lourenço', 'Graziane Sales Teodoro'] ,
    "GMM108_11A13A21A": ['Jailton Viana da Conceição', 'Jamil Gomes de Abreu Junior', 'Thais Presses Mendes'] ,
    "GMM109_15A18A": ['Fernando Augusto Naves', 'Rita de Cássia Dornelas Sodré'] ,
    "GMM116_2A": ['Marcio Fialho Chaves', 'Marlon Pimenta Fonseca'] ,
    "GMM130_31A31B32A32B": ['Marcio Fialho Chaves', 'Ana Carolina Dias do Amaral Ramos'] ,
    "GMM135_10A": ['Andreza Cristina Beezão Moreira', 'Tiago de Medeiros Vieira'] 
}

def compara(solucao1, solucao2):
    apenas_no_solucao1 = {}
    apenas_no_solucao2 = {}
    for i in range(len(solucao1)):

        doc_nome = solucao1[i]["nome"]
        apenas_no_solucao1[doc_nome] = []
        apenas_no_solucao2[doc_nome] = []

        for dis in solucao1[i]['disciplinas']:
            if not dis in solucao2[i]['disciplinas']:
                apenas_no_solucao1[doc_nome].append(dis)

        for dis in solucao2[i]['disciplinas']:
            if not dis in solucao1[i]['disciplinas']:
                apenas_no_solucao2[doc_nome].append(dis)

        if apenas_no_solucao1[doc_nome] == []:
            apenas_no_solucao1.pop(doc_nome)
        if apenas_no_solucao2[doc_nome] == []:
            apenas_no_solucao2.pop(doc_nome)


    for i in range(len(solucao1)):
        doc_nome = solucao1[i]["nome"]
        if ((doc_nome in apenas_no_solucao2) or 
            (doc_nome in apenas_no_solucao1)):
            print("\n", doc_nome)

        if doc_nome in apenas_no_solucao1:
            print("apenas_no_solucao1:", apenas_no_solucao1[doc_nome])

        if doc_nome in apenas_no_solucao2:
            print("apenas_no_solucao2:",apenas_no_solucao2[doc_nome])
      

def analisa_respeitou_ranking(solucao1):
    respeitou = True
    for doc in solucao1:
        for dis in doc["disciplinas"]:
            if dis in rankings and rankings[dis][0] != doc["nome"]:
                print("Nao atendeu", dis, doc["nome"])
                respeitou = False
    if respeitou:
        print("Não houveram infrações no ranking")




# with open('analise2/horario_res_com_des.json', 'r') as file:
#     sol_padrao = json.load(file)

# with open('analise2/horario_opt_com_des.json', 'r') as file:
#     sol_alternativa = json.load(file)
# compara(sol_padrao, sol_alternativa)

# with open('analise2/horario_res_sem_des.json', 'r') as file:
#     sol_alternativa = json.load(file)
# compara(sol_padrao, sol_alternativa)


# with open('analise4_repesado/h_res_com_des_repesado.json', 'r') as file:
#     sol_alternativa = json.load(file)
# compara(sol_padrao, sol_alternativa)

# analisa_respeitou_ranking(sol_padrao)
# print()
# analisa_respeitou_ranking(sol_alternativa)
# print()
with open('solucao.json', 'r') as file:
    sol_padrao = json.load(file)
# compara(sol_padrao, sol_alternativa)
analisa_respeitou_ranking(sol_padrao)
print()
# with open('analise4_repesado/h_res_com_des_repesado.json', 'r') as file:
#     sol_alternativa = json.load(file)

# with open('analise4_repesado/h_opt_com_des_repesado.json', 'r') as file:
#     horario_opt = json.load(file)
# with open('analise2_com_des/horario_opt.json', 'r') as file:
#     horario_res = json.load(file)
# compara(horario_opt, horario_res)

# with open('analise4_repesado/h_opt_com_des_repesado.json', 'r') as file:
#     horario_opt = json.load(file)
# with open('analise2_com_des/horario_opt.json', 'r') as file:
#     horario_res = json.load(file)
# compara(horario_opt, horario_res)
