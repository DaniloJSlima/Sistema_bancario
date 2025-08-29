import textwrap
from abc import ABC, abstractmethod
from datetime import datetime


class Cliente:
    def __init__(self, endereco):
        self.endereco = endereco
        self.contas = []

    def realizar_transacao(self, conta, transacao):
        sucesso, msg = transacao.registrar(conta)
        print(msg)

    def adicionar_conta(self, conta):
        self.contas.append(conta)


class PessoaFisica(Cliente):
    def __init__(self, nome, data_nascimento, cpf, endereco):
        super().__init__(endereco)
        self.nome = nome
        self.data_nascimento = data_nascimento
        self.cpf = cpf


class Conta:
    def __init__(self, numero, cliente):
        self._saldo = 0
        self._numero = numero
        self._agencia = "0001"
        self._cliente = cliente
        self._historico = Historico()

    @classmethod
    def nova_conta(cls, cliente, numero):
        return cls(numero, cliente)

    @property
    def saldo(self):
        return self._saldo

    @property
    def numero(self):
        return self._numero

    @property
    def agencia(self):
        return self._agencia

    @property
    def cliente(self):
        return self._cliente

    @property
    def historico(self):
        return self._historico

    def sacar(self, valor):
        if valor <= 0:
            return False, "Valor inválido para saque. Informe um valor maior que zero."
        if valor > self._saldo:
            return False, f"Saldo insuficiente! Você tentou sacar R$ {valor:.2f}, mas tem apenas R$ {self._saldo:.2f} disponível."

        self._saldo -= valor
        return True, f"Saque de R$ {valor:.2f} realizado com sucesso!"

    def depositar(self, valor):
        if valor <= 0:
            return False, "Valor inválido para depósito. Informe um valor maior que zero."

        self._saldo += valor
        return True, f"Depósito de R$ {valor:.2f} realizado com sucesso!"


class ContaCorrente(Conta):
    def __init__(self, numero, cliente, limite=500, limite_saques=3):
        super().__init__(numero, cliente)
        self._limite = limite
        self._limite_saques = limite_saques

    def sacar(self, valor):
        numero_saques = len(
            [t for t in self.historico.transacoes if t["tipo"] == Saque.__name__]
        )

        if valor > self._limite:
            return False, "O valor do saque excede o limite permitido de R$ {self._limite:.2f}."
        if numero_saques >= self._limite_saques:
            return False, "Você já atingiu o número máximo de {self._limite_saques} saques permitidos."

        return super().sacar(valor)

    def __str__(self):
        return f"""\
            Agência:\t{self.agencia}
            C/C:\t\t{self.numero}
            Titular:\t{self.cliente.nome}
        """


class Historico:
    def __init__(self):
        self._transacoes = []

    @property
    def transacoes(self):
        return self._transacoes

    def adicionar_transacao(self, transacao):
        self._transacoes.append(
            {
                "tipo": transacao.__class__.__name__,
                "valor": transacao.valor,
                "data": datetime.now().strftime("%d-%m-%Y %H:%M:%S"),
            }
        )


class Transacao(ABC):
    @property
    @abstractmethod
    def valor(self):
        pass

    @abstractmethod
    def registrar(self, conta):
        pass


class Saque(Transacao):
    def __init__(self, valor):
        self._valor = valor

    @property
    def valor(self):
        return self._valor

    def registrar(self, conta):
        sucesso, msg = conta.sacar(self.valor)
        if sucesso:
            conta.historico.adicionar_transacao(self)
        return sucesso, msg


class Deposito(Transacao):
    def __init__(self, valor):
        self._valor = valor

    @property
    def valor(self):
        return self._valor

    def registrar(self, conta):
        sucesso, msg = conta.depositar(self.valor)
        if sucesso:
            conta.historico.adicionar_transacao(self)
        return sucesso, msg


def menu():
    menu = """\n
    [1]\tDepositar
    [2]\tSacar
    [3]\tExtrato
    [4]\tNova conta
    [5]\tListar contas
    [6]\tNovo usuário
    [q]\tSair
    => """
    return input(textwrap.dedent(menu))


def filtrar_cliente(cpf, clientes):
    return next((c for c in clientes if c.cpf == cpf), None)


def recuperar_conta_cliente(cliente):
    if not cliente.contas:
        print("\nCliente não possui conta cadastrada.")
        return
    return cliente.contas[0] 


def realizar_transacao(clientes, transacao_cls):
    cpf = input("Informe o CPF do cliente: ")
    cliente = filtrar_cliente(cpf, clientes)

    if not cliente:
        print("\n Cliente não encontrado!")
        return

    try:
        valor = float(input("Informe o valor: "))
    except ValueError:
        print("\n Entrada inválida. Digite um número.")
        return

    conta = recuperar_conta_cliente(cliente)
    if conta:
        transacao = transacao_cls(valor)
        cliente.realizar_transacao(conta, transacao)


def exibir_extrato(clientes):
    cpf = input("Informe o CPF do cliente: ")
    cliente = filtrar_cliente(cpf, clientes)

    if not cliente:
        print("\n Cliente não encontrado! ")
        return

    conta = recuperar_conta_cliente(cliente)
    if not conta:
        return

    print("\n================ EXTRATO ================")
    transacoes = conta.historico.transacoes

    extrato = "\n".join(
        f"{t['data']} - {t['tipo']}: R$ {t['valor']:.2f}"
        for t in transacoes
    ) or "Não foram realizadas movimentações."

    print(extrato)
    print(f"\nSaldo:\n\tR$ {conta.saldo:.2f}")


def criar_cliente(clientes):
    cpf = input("Informe o CPF (somente número): ")
    if filtrar_cliente(cpf, clientes):
        print("\n Já existe cliente com esse CPF!")
        return

    nome = input("Informe o nome completo: ")
    data_nascimento = input("Informe a data de nascimento (dd-mm-aaaa): ")
    endereco = input("Informe o endereço: ")

    clientes.append(PessoaFisica(nome, data_nascimento, cpf, endereco))
    print("\nCliente criado com sucesso!")


def criar_conta(numero_conta, clientes, contas):
    cpf = input("Informe o CPF do cliente: ")
    cliente = filtrar_cliente(cpf, clientes)

    if not cliente:
        print("\nCliente não encontrado!")
        return

    conta = ContaCorrente.nova_conta(cliente=cliente, numero=numero_conta)
    contas.append(conta)
    cliente.adicionar_conta(conta)

    print("\nConta criada com sucesso!")


def listar_contas(contas):
    for conta in contas:
        print("=" * 100)
        print(textwrap.dedent(str(conta)))


def main():
    clientes, contas = [], []

    opcoes = {
        "1": lambda: realizar_transacao(clientes, Deposito),
        "2": lambda: realizar_transacao(clientes, Saque),
        "3": lambda: exibir_extrato(clientes),
        "4": lambda: criar_cliente(clientes),
        "5": lambda: criar_conta(len(contas) + 1, clientes, contas),
        "6": lambda: listar_contas(contas),
    }

    while True:
        opcao = menu()
        if opcao == "q":
            break
        acao = opcoes.get(opcao)
        acao() if acao else print("\n@@@ Operação inválida! @@@")


main()
