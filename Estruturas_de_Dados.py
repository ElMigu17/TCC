

class disciplina:
    def __init__(self, pos: int, codigo: str, qtd_creditos: int, horarios: list, eh_graduacao: bool, turmas: list) -> None:
        self.pos = pos
        self.codigo = codigo
        self.qtd_creditos = qtd_creditos
        self.docente = None
        self.horarios = horarios
        self.eh_graduacao = eh_graduacao
        self.turmas = turmas
    
    def show(self):
        print(self.id, self.codigo, self.qtd_creditos, self.docente, self.horarios, self.eh_graduacao, self.turmas)


class docente:
    def __init__(self, pos:int, nome: str, siape: int) -> None:
        self.pos = pos
        self.nome = nome
        self.siape = siape
        self.num_disc_anterior = 0
        self.estudantes_fim_anterior = 0
        self.qtd_credito_anterior = 0
        self.preferencia = {}
        self.discplinas = []
        self.disc_per_1 = []  #disciplina periodo -1
        self.disc_per_2 = []
        self.disc_per_3 = []
    
    def add_info_ultimo_periodo(self, num_disc_anterior, estudantes_fim_anterior, qtd_credito_anterior):
        self.num_disc_anterior = num_disc_anterior
        self.estudantes_fim_anterior = estudantes_fim_anterior
        self.qtd_credito_anterior = qtd_credito_anterior

    def add_preferencia(self, peso, nome):
        self.preferencia[peso] = nome

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