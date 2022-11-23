"""Nurse scheduling problem with shift requests."""
from ortools.sat.python import cp_model

class disciplina:
    def __init__(self, qtd_creditos, nome, codigo, horarios, eh_graduacao: bool, turmas) -> None:
        self.qtd_creditos = qtd_creditos
        self.nome = nome
        self.codigo = codigo
        self.docente = None
        self.horarios = horarios
        self.eh_graduacao = eh_graduacao
        self.turmas = turmas

class docente:
    def __init__(self, nome, id) -> None:
        self.nome = nome
        self.id = id
        self.discplinas = []
        self.disc_per_1 = []  #disciplina periodo -1
        self.disc_per_2 = []
        self.disc_per_3 = []
    
    def discplinas_com_preferencia(self):
        #TODO
        return None

class distribuicao_graduacao:

    def leitura_disciplinas(self):
        disciplinas = [
            disciplina(2, 'teste', 'GMM101', {2: 15}, True, ['9A']),
            disciplina(2, 'teste', 'GMM101', {5: 19}, True, ['26A']),
            disciplina(4, 'teste', 'GMM102', {5: 7, 4: 9}, True, ['13A', '10A', '21A']),
            disciplina(4, 'teste', 'GMM102', {2: 7, 5: 7}, True, ['30C', '30A']),
            disciplina(6, 'teste', 'GMM104', {1: 8, 3: 8, 5: 8}, True, ['30G', '30E'])
        ]

        return disciplinas

    def leitura_docentes(self):
        docentes = [
            docente("claudin", 123456),
            docente("roger", 654321),
            docente("scub", 342516)
        ]

        return docentes
        
    def principal(self):
        self.distribui_disciplinas_com_prioridade()
        self.distribui_restante()


    def calcula(self):
        # This program tries to find an optimal assignment of nurses to shifts
        # (3 shifts per day, for 7 days), subject to some constraints (see below).
        # Each nurse can request to be assigned to specific shifts.
        # The optimal assignment maximizes the number of fulfilled shift requests.
        num_docente = 5
        num_dias = 5
        all_docentes = range(num_docente)
        all_shifts = range(num_shifts)
        all_days = range(num_days)
        shift_requests = [[[0, 0, 1], [0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 1], [0, 1, 0], [0, 0, 1]],
                        [[0, 0, 0], [0, 0, 0], [0, 1, 0], [0, 1, 0], [1, 0, 0], [0, 0, 0], [0, 0, 1]],
                        [[0, 1, 0], [0, 1, 0], [0, 0, 0], [1, 0, 0], [0, 0, 0], [0, 1, 0], [0, 0, 0]],
                        [[0, 0, 1], [0, 0, 0], [1, 0, 0], [0, 1, 0], [0, 0, 0], [1, 0, 0], [0, 0, 0]],
                        [[0, 0, 0], [0, 0, 1], [0, 1, 0], [0, 0, 0], [1, 0, 0], [0, 1, 0], [0, 0, 0]]]

        # Creates the model.
        model = cp_model.CpModel()

        # Creates shift variables.
        # shifts[(n, d, s)]: nurse 'n' works shift 's' on day 'd'.
        # cria uma variavel para cada disciplina e doscente
        disciplinas = self.leitura_disciplinas()
        docentes = self.leitura_docentes()

        # Each shift is assigned to exactly one nurse in .
        # Restrição de que só um pode dar aula
        for d in disciplina:
            model.Add()

        # Each nurse works at most one shift per day.
        # restrição de no minimo 8 creditos
        for d in all_docentes:
            model.Add(8 <=  sum(d.discplinas))

        # Try to distribute the shifts evenly, so that each nurse works
        # min_shifts_per_nurse shifts. If this is not possible, because the total
        # number of shifts is not divisible by the number of nurses, some nurses will
        # be assigned one more shift.
        min_shifts_per_nurse = (num_shifts * num_days) // num_nurses
        if num_shifts * num_days % num_nurses == 0:
            max_shifts_per_nurse = min_shifts_per_nurse
        else:
            max_shifts_per_nurse = min_shifts_per_nurse + 1
        for n in all_nurses:
            num_shifts_worked = 0
            for d in all_days:
                for s in all_shifts:
                    num_shifts_worked += shifts[(n, d, s)]
            model.Add(min_shifts_per_nurse <= num_shifts_worked)
            model.Add(num_shifts_worked <= max_shifts_per_nurse)

        # pylint: disable=g-complex-comprehension
        model.Maximize(
            sum(shift_requests[n][d][s] * shifts[(n, d, s)] for n in all_nurses
                for d in all_days for s in all_shifts))

        # Creates the solver and solve.
        solver = cp_model.CpSolver()
        status = solver.Solve(model)

        if status == cp_model.OPTIMAL:
            print('Solution:')
            for d in all_days:
                print('Day', d)
                for n in all_nurses:
                    for s in all_shifts:
                        if solver.Value(shifts[(n, d, s)]) == 1:
                            if shift_requests[n][d][s] == 1:
                                print('Nurse', n, 'works shift', s, '(requested).')
                            else:
                                print('Nurse', n, 'works shift', s,
                                    '(not requested).')
                print()
            print(f'Number of shift requests met = {solver.ObjectiveValue()}',
                f'(out of {num_nurses * min_shifts_per_nurse})')
        else:
            print('No optimal solution found !')

        # Statistics.
        print('\nStatistics')
        print('  - conflicts: %i' % solver.NumConflicts())
        print('  - branches : %i' % solver.NumBranches())
        print('  - wall time: %f s' % solver.WallTime())
        for s in shifts:
            print(s, s==1);


def main():

if __name__ == '__main__':
    main()
