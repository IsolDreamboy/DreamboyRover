


class Terra:
    def __init__(self, largura=20,altura=20):
        self.largura = largura
        self.altura= altura
        self.grid = [[0 for _ in  range(largura)] for _ in range(altura)]



        self.grid[2][2]= 1
        self.grid[5][5]=1

    def posicao_valida(self,x,y):
        if x < 0 or x >= self.largura or if y < 0 or y >= self.altura:
            return False, "Você está fora dos limites, erro."

        if self.grid[y][x]== 1:
            return False, "Obstáculo, desvie."

        return True, "ok!"