import time
import math
import random

def teste_tempo_modulo():
    def calculo_modulo1(i: float) -> float:
        if i < 0:
            return -i
        else:
            return i

    def calculo_modulo2(i: float) -> float:
        return math.sqrt(i*i)

    def teste_tempo(funcao):
        inicio = time.time()
        qtd_dif = 0
        for i in range(10000000):
            num = random.random()
            if (num - funcao(num)) != 0:
                qtd_dif += 1
        fim = time.time()
        if qtd_dif != 0:
            print("qtd_dif:", qtd_dif)
        return fim - inicio

    print("MODULO1:")
    tempo = 0
    random.seed(10)
    for i in range(100):
        tempo += teste_tempo(calculo_modulo1)
    print("media_tempo:", tempo/100)
    print("MODULO2:")
    tempo = 0
    random.seed(10)
    for i in range(100):
        tempo += teste_tempo(calculo_modulo2)
    print("media_tempo:", tempo/100)