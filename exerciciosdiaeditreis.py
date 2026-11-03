"""Fila de Prioridades (min-heap sem heapq) e Tabela Hash com encadeamento separado."""


# ============================================================
# 1) FILA DE PRIORIDADES (min-heap em lista, desempate FIFO)
# ============================================================
class FilaPrioridade:
    def __init__(self):
        # cada elemento: (prioridade, ordem_de_chegada, item)
        self._heap = []
        self._contador = 0

    @staticmethod
    def _menor(a, b):
        # menor prioridade vence; empate -> menor ordem de chegada (FIFO)
        return (a[0], a[1]) < (b[0], b[1])

    def inserir(self, item, prioridade):
        self._heap.append((prioridade, self._contador, item))
        self._contador += 1
        self._subir(len(self._heap) - 1)

    def remover(self):
        if self.esta_vazia():
            raise IndexError("fila vazia")
        h = self._heap
        h[0], h[-1] = h[-1], h[0]
        topo = h.pop()
        if h:
            self._descer(0)
        return topo[2]

    def espiar(self):
        if self.esta_vazia():
            raise IndexError("fila vazia")
        return self._heap[0][2]

    def esta_vazia(self):
        return len(self._heap) == 0

    def __len__(self):
        return len(self._heap)

    def _subir(self, i):
        h = self._heap
        while i > 0:
            pai = (i - 1) // 2
            if self._menor(h[i], h[pai]):
                h[i], h[pai] = h[pai], h[i]
                i = pai
            else:
                break

    def _descer(self, i):
        h = self._heap
        n = len(h)
        while True:
            esq, dir_ = 2 * i + 1, 2 * i + 2
            menor = i
            if esq < n and self._menor(h[esq], h[menor]):
                menor = esq
            if dir_ < n and self._menor(h[dir_], h[menor]):
                menor = dir_
            if menor == i:
                break
            h[i], h[menor] = h[menor], h[i]
            i = menor


def simular_escalonador(tarefas):
    """tarefas: lista de (nome, prioridade, duracao). Retorna (esperas, media)."""
    fila = FilaPrioridade()
    for nome, prioridade, duracao in tarefas:
        fila.inserir((nome, duracao), prioridade)

    tempo = 0
    esperas = []
    while not fila.esta_vazia():
        nome, duracao = fila.remover()
        esperas.append((nome, tempo))  # espera = instante em que começa a rodar
        tempo += duracao
    media = sum(e for _, e in esperas) / len(esperas) if esperas else 0.0
    return esperas, media


# ============================================================
# 2) TABELA HASH (encadeamento separado, redimensionamento)
# ============================================================
class TabelaHash:
    FATOR_MAX = 0.75

    def __init__(self, capacidade=8):
        self._capacidade = capacidade
        self._baldes = [[] for _ in range(capacidade)]
        self._tamanho = 0

    @staticmethod
    def hash_string(s):
        # hash polinomial (base 31), limitado a 32 bits; sem usar hash()
        h = 0
        for c in s:
            h = (h * 31 + ord(c)) & 0xFFFFFFFF
        return h

    def _indice(self, chave):
        return self.hash_string(chave) % self._capacidade

    def colocar(self, chave, valor):
        balde = self._baldes[self._indice(chave)]
        for par in balde:
            if par[0] == chave:
                par[1] = valor  # atualiza
                return
        balde.append([chave, valor])
        self._tamanho += 1
        if self._tamanho / self._capacidade > self.FATOR_MAX:
            self._redimensionar()

    def obter(self, chave, padrao=None):
        for k, v in self._baldes[self._indice(chave)]:
            if k == chave:
                return v
        return padrao

    def remover(self, chave):
        balde = self._baldes[self._indice(chave)]
        for i, (k, _) in enumerate(balde):
            if k == chave:
                valor = balde.pop(i)[1]
                self._tamanho -= 1
                return valor
        raise KeyError(chave)

    def contem(self, chave):
        return any(k == chave for k, _ in self._baldes[self._indice(chave)])

    def __len__(self):
        return self._tamanho

    def itens(self):
        for balde in self._baldes:
            for k, v in balde:
                yield k, v

    def _redimensionar(self):
        antigos = self._baldes
        self._capacidade *= 2
        self._baldes = [[] for _ in range(self._capacidade)]
        for balde in antigos:
            for k, v in balde:
                self._baldes[self._indice(k)].append([k, v])  # rehash


def frequencia_palavras(texto):
    tabela = TabelaHash()
    palavras = "".join(c.lower() if c.isalnum() else " " for c in texto).split()
    for p in palavras:
        tabela.colocar(p, tabela.obter(p, 0) + 1)
    return tabela


# ============================================================
# Demonstração
# ============================================================
if __name__ == "__main__":
    print("=== Fila de prioridades ===")
    f = FilaPrioridade()
    f.inserir("C", 2)
    f.inserir("A", 1)
    f.inserir("B", 1)  # empate com A: A chegou antes
    print("espiar:", f.espiar(), "| len:", len(f))
    print("ordem:", [f.remover() for _ in range(len(f))])

    print("\n=== Escalonador de CPU ===")
    tarefas = [("T1", 3, 5), ("T2", 1, 3), ("T3", 2, 8), ("T4", 1, 6), ("T5", 4, 2)]
    esperas, media = simular_escalonador(tarefas)
    for nome, e in esperas:
        print(f"{nome}: espera = {e}")
    print(f"Tempo médio de espera = {media:.2f}")

    print("\n=== Tabela hash: alunos ===")
    alunos = TabelaHash()
    for mat, nome in [("2021001", "Ana"), ("2021002", "Bruno"), ("2021003", "Carla"),
                      ("2021004", "Diego"), ("2021005", "Eva"), ("2021006", "Fábio"),
                      ("2021007", "Gabi"), ("2021008", "Hugo")]:
        alunos.colocar(mat, nome)
    print("len:", len(alunos), "| capacidade:", alunos._capacidade)
    print("2021003 ->", alunos.obter("2021003"))
    print("contem 9999999?", alunos.contem("9999999"))
    alunos.remover("2021002")
    print("após remover 2021002, len:", len(alunos))

    print("\n=== Tabela hash: frequência de palavras ===")
    texto = "O gato viu o rato. O rato fugiu e o gato dormiu."
    freq = frequencia_palavras(texto)
    for p, c in sorted(freq.itens(), key=lambda x: (-x[1], x[0])):
        print(f"{p}: {c}")

    print("""
=== Respostas teóricas ===
Complexidade (heap com n elementos, altura ~ log2 n):
 - inserir: O(log n). Entra no fim e sobe (sift-up) no máximo a altura da árvore.
 - remover: O(log n). Troca raiz com o último, remove e desce (sift-down) no máximo a altura.
 - espiar / esta_vazia / len: O(1).

Colisão: duas chaves diferentes cujo hash cai no mesmo índice do vetor. É inevitável
(há mais chaves possíveis que posições). No encadeamento separado, cada posição guarda
uma lista com as chaves que colidiram.

Redimensionamento: com mais elementos por balde, as listas crescem e as operações deixam
de ser O(1) e tendem a O(n). Ao passar do fator de carga 0,75 dobra-se a capacidade e
reinserem-se todas as chaves (rehash, pois índice = hash % capacidade muda), mantendo as
listas curtas e o custo médio O(1) amortizado.
""")