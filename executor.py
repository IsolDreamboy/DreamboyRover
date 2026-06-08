from typing import List
from AST import ASTEngine, FlatAction
from parser import compilar

DIRECOES = ["N", "L", "S", "O"]
PASSOS = {"N": (0, 1), "S": (0, -1), "L": (1, 0), "O": (-1, 0)}


class Rover:
    def __init__(self, x: int = 0, y: int = 0, direcao: str = "N"):
        if not (0 <= x < 10 and 0 <= y < 10):
            raise ValueError(f"Coordenadas inválidas ({x}, {y}). Devem estar entre 0 e 9.")
        if direcao not in DIRECOES:
            raise ValueError(f"Direção inválida '{direcao}'. Use: {DIRECOES}")
        self.x = x
        self.y = y
        self.direcao = direcao

    def turn(self, lado: str):
        idx = DIRECOES.index(self.direcao)
        offset = 1 if lado == "DIREITA" else -1
        self.direcao = DIRECOES[(idx + offset) % 4]


class Grid:
    def verificar_obstaculo(self, x: int, y: int) -> bool:
        return x == 1 and y == 1

    def limites_validos(self, x: int, y: int) -> bool:
        return 0 <= x < 10 and 0 <= y < 10


class RoverExecutor:
    def __init__(self, rover: Rover, grid: Grid):
        self.rover = rover
        self.grid = grid
        self.logs: List[str] = []

    def log(self, mensagem: str):
        print(mensagem)
        self.logs.append(mensagem)

    def _proxima_posicao(self, reverso: bool = False) -> tuple:
        dx, dy = PASSOS[self.rover.direcao]
        if reverso:
            return self.rover.x - dx, self.rover.y - dy
        return self.rover.x + dx, self.rover.y + dy

    def _executar_movimento(self, passos: int = 1, reverso: bool = False):
        """Lógica unificada para MOVER e RECUAR, com N passos."""
        label = "Recuar" if reverso else "Mover"
        for i in range(passos):
            nx, ny = self._proxima_posicao(reverso)

            if not self.grid.limites_validos(nx, ny):
                self.log(f"[ERRO] {label} inválido: fora dos limites em ({nx}, {ny}).")
                return
            elif self.grid.verificar_obstaculo(nx, ny):
                self.log(f"[AVISO] {label} bloqueado: obstáculo em ({nx}, {ny}).")
                return
            else:
                self.rover.x, self.rover.y = nx, ny
                self.log(f"[SUCESSO] {label} (passo {i+1}/{passos}): Rover em ({self.rover.x}, {self.rover.y}).")

    def tem_obstaculo_a_frente(self) -> bool:
        """Callback para o ASTEngine verificar obstáculos no SE_OBSTACULO."""
        nx, ny = self._proxima_posicao()
        return self.grid.verificar_obstaculo(nx, ny)

    def executar_acao(self, acao: FlatAction):
        """Executa uma FlatAction vinda do ASTEngine."""
        match acao.action:
            case "MOVER":
                self._executar_movimento(passos=acao.value or 1, reverso=False)

            case "RECUAR":
                self._executar_movimento(passos=acao.value or 1, reverso=True)

            case "ESQUERDA" | "DIREITA":
                self.rover.turn(acao.action)
                self.log(f"[SUCESSO] Giro: {acao.action}. Direção: {self.rover.direcao}.")

            case "ESCANEAR":
                nx, ny = self._proxima_posicao()
                status = "OBSTÁCULO" if self.grid.verificar_obstaculo(nx, ny) else "LIMPA"
                self.log(f"[SCAN] Célula à frente ({nx}, {ny}): {status}.")

            case _:
                self.log(f"[ERRO] Ação desconhecida: {acao.action}")


def ler_input() -> str:
    """Lê o script de comandos do Rover via input do terminal."""
    print("=" * 50)
    print("  INTERPRETADOR DO ROVER")
    print("=" * 50)

    # Coordenadas iniciais
    while True:
        try:
            entrada = input("\nPosição inicial (x y direção) [padrão: 0 0 N]: ").strip()
            if not entrada:
                x, y, direcao = 0, 0, "N"
            else:
                partes = entrada.split()
                if len(partes) != 3:
                    print("[ERRO] Formato: x y direção (ex: 2 3 L)")
                    continue
                x, y, direcao = int(partes[0]), int(partes[1]), partes[2].upper()
            rover = Rover(x, y, direcao)
            break
        except ValueError as e:
            print(f"[ERRO] {e}")

    # Script de comandos
    print("\nDigite o script de comandos (linha vazia para finalizar):")
    print("Exemplo: MOVER 3, ESQUERDA, REPETIR 2 { MOVER 1 }")
    print("-" * 50)

    linhas = []
    while True:
        try:
            linha = input()
            if linha.strip() == "":
                break
            linhas.append(linha)
        except EOFError:
            break

    codigo = "\n".join(linhas)
    return rover, codigo


if __name__ == "__main__":
    rover, codigo = ler_input()
    grid = Grid()
    executor = RoverExecutor(rover, grid)

    print(f"\n{'=' * 50}")
    print(f"  Rover iniciando em ({rover.x}, {rover.y}) -> {rover.direcao}")
    print(f"{'=' * 50}\n")

    try:
        # Lexer -> Parser -> AST
        ast_nodes = compilar(codigo)

        # AST -> FlatActions -> Executor
        for acao in ASTEngine.execute(ast_nodes, verificar_obstaculo=executor.tem_obstaculo_a_frente):
            executor.executar_acao(acao)

    except Exception as e:
        print(f"\n[ERRO FATAL] {e}")

    print(f"\n{'=' * 50}")
    print(f"  Rover finalizou em ({rover.x}, {rover.y}) -> {rover.direcao}")
    print(f"{'=' * 50}")

    print(f"\n--- Histórico ({len(executor.logs)} ações) ---")
    for entry in executor.logs:
        print(f"  {entry}")