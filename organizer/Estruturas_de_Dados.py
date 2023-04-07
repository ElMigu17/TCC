import json
from datetime import date
import os

class disciplina:
    def __init__(self, *args) -> None:
        if type(args[0]) == dict:
            self.dict_to_disciplina(args[0])
        else:
            self.init_pequeno(args[0], args[1], args[2], args[3], args[4], args[5])

    def init_pequeno(self, pos: int, codigo: str, qtd_creditos: int, horarios: list, eh_graduacao: bool, turmas: list):
        self.pos = pos
        self.codigo = codigo
        self.qtd_creditos = qtd_creditos
        self.docente = None
        self.horarios = horarios
        self.eh_graduacao = eh_graduacao
        self.turmas = turmas

    def dict_to_disciplina(self, my_dict):
        for key in my_dict:
            setattr(self, key, my_dict[key])

    def show(self):
        print(self.pos, self.codigo, self.qtd_creditos, self.docente, self.horarios, self.eh_graduacao, self.turmas)

    def string_cod_turma(self):
        turmas = self.turmas
        turmas.sort()
        turmas_as_string = ""
        for turma in turmas:
            turmas_as_string += turma
        return self.codigo + "_" + turmas_as_string  


class docente:
    def __init__(self, *args) -> None:
        if type(args[0]) == dict:
            self.dict_to_docente(args[0])
        else:
            self.init_pequeno(args[0], args[1], args[2], args[3])

    def init_pequeno(self, pos:int, nome: str, siape: int, reducao: int):
        self.pos = pos
        self.nome = nome
        self.siape = siape
        self.num_disc_anterior = 0
        self.estudantes_fim_anterior = 0
        self.qtd_credito_anterior = 0
        self.reducao = reducao
        self.preferencia = {}
        self.disciplinas = []
        self.disc_per_1 = []  #disciplina periodo -1
        self.disc_per_2 = []
        self.disc_per_3 = []
    

    def dict_to_docente(self, my_dict):
        for key in my_dict:
            setattr(self, key, my_dict[key])

    
    def add_info_ultimo_periodo(self, num_disc_anterior, estudantes_fim_anterior, qtd_credito_anterior):
        self.num_disc_anterior = num_disc_anterior
        self.estudantes_fim_anterior = estudantes_fim_anterior
        self.qtd_credito_anterior = qtd_credito_anterior

    def add_preferencia(self, peso, nome) -> None:
        self.preferencia[nome] = peso

    def tem_mais_preferencia_que(self, doc, cod_turma) -> bool:
        if self.num_disc_anterior > doc.num_disc_anterior:
            return True
        elif self.num_disc_anterior < doc.num_disc_anterior:
            return False
        
        if self.estudantes_fim_anterior > doc.estudantes_fim_anterior:
            return True
        elif self.estudantes_fim_anterior > doc.estudantes_fim_anterior:
            return False

        if self.ultima_vez_que_ministrou(cod_turma) == doc.ultima_vez_que_ministrou(cod_turma):
            return doc.nome < self.nome
    
    def ultima_vez_que_ministrou(self, cod_turma) -> int:
        
        if cod_turma in self.disc_per_1:
            return 1
        if cod_turma in self.disc_per_2:
            return 2
        if cod_turma in self.disc_per_3:
            return 3
        return 4



class array_manipulator:

    def ano_semestre(self) -> str:
        hoje = date.today()
        semestre = int(hoje.month/7) + 1
        
        return str(hoje.year) + "-" + str(semestre)

    def array_object_to_dict(self, array):
        my_dict = []
        for i in array:
            my_dict.append(i.__dict__)
        return my_dict

    def save_as_json(self, array: list, saida: bool = False):
        nome_arquivo = "disciplina"
        if type(array[0]) == docente:
            nome_arquivo = "docente"

        if saida:
            nome_arquivo += "_saida"
        nome_arquivo += self.ano_semestre()  
        path_saves = os.getcwd() + "/saves"
        out = self.array_object_to_dict(array)
        print("Salvando no arquivo: " + nome_arquivo)

        try:
            os.listdir(path_saves)
        except FileNotFoundError:
            os.mkdir(path_saves)

        with open(path_saves + "/" + nome_arquivo + ".json", "w") as outfile:
            json.dump(out, outfile)
    
    def get_json(self, nome_arquivo:str) -> list:
        path_saves = os.getcwd() + "/saves"
        array_of_objects = []
        
        with open(path_saves + "/" + nome_arquivo + ".json", "r") as outfile:
            json_object = json.load(outfile)

        class_type = docente
        if "codigo" in json_object[0]:
            class_type = disciplina

        for obj in json_object:
            array_of_objects.append(class_type(obj))

        return array_of_objects