from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

# Modelo de usuário com nome, renda e dívidas
class User(BaseModel):
    nome: str
    renda: float
    dividas: int = 0

# Lista que simula o "banco de dados" de usuários
usuarios = []

# Função que calcula o score de crédito do usuário
def calcula_score(renda, dividas):
    score = (renda / (dividas + 1)) * 10
    return max(300, min(900, int(score)))  # sempre entre 300 e 900

# Endpoint para cadastro de usuários
@app.post("/cadastro")
def cadastro(user: User):
    score = calcula_score(user.renda, user.dividas)
    usuario = user.dict()
    usuario["score"] = score
    usuario["saldo_reais"] = 0.0
    usuario["saldo_crypto"] = 0.0
    usuarios.append(usuario)
    return {"msg": f"Usuario {user.nome} cadastrado com sucesso!", "data": usuario}

# Endpoint para listar todos os usuários cadastrados
@app.get("/usuarios")
def listar_usuarios():
    return {"usuarios": usuarios}

# Modelo para solicitação de empréstimo
class Emprestimo(BaseModel):
    nome: str
    valor: float

# Lista que simula os empréstimos
emprestimos = []

# Endpoint para solicitar empréstimo
@app.post("/emprestimo")
def solicitar_emprestimo(pedido: Emprestimo):
    usuario = next((u for u in usuarios if u["nome"] == pedido.nome), None)
    if not usuario:
        return {'erro': "Usuário não encontrado!"}

    # Define a taxa com base no score
    score = usuario["score"]
    if score >= 700:
        taxa = 0.02
    elif score >= 500:
        taxa = 0.05
    else:
        taxa = 0.1

    # Cria o registro do empréstimo
    emprestimo = {
        "usuario": pedido.nome,
        "valor": pedido.valor,
        "score": score,
        "taxa": taxa,
        "status": "aguardando investidor"
    }
    emprestimos.append(emprestimo)

    return {
        "msg": f"Empréstimo solicitado por {pedido.nome}",
        "dados": emprestimo
    }

# Endpoint para listar todos os empréstimos
@app.get("/emprestimos")
def listar_emprestimos():
    return {"emprestimos": emprestimos}

# Modelo para aprovação de empréstimo
class AprovarEmprestimo(BaseModel):
    indice: int
    investidor: str

# Endpoint para aprovar empréstimo
@app.post("/aprovar")
def aprovar_emprestimo(dados: AprovarEmprestimo):
    if dados.indice < 0 or dados.indice >= len(emprestimos):
        return {"erro": "Empréstimo não encontrado"}

    emprestimo = emprestimos[dados.indice]

    if emprestimo["status"] != "aguardando investidor":
        return {"erro": "Este empréstimo já foi processado"}

    # Atualiza o status e registra o investidor
    emprestimo["status"] = "aprovado"
    emprestimo["investidor"] = dados.investidor

    return {
        "msg": f"Empréstimo aprovado por {dados.investidor}",
        "emprestimo": emprestimo
    }

# Modelo para pagamento de empréstimo
class Pagamento(BaseModel):
    indice: int
    parcelas: int

# Endpoint para pagar empréstimo
@app.post("/pagar")
def pagar_emprestimo(dados: Pagamento):
    if dados.indice < 0 or dados.indice >= len(emprestimos):
        return {"erro": "Empréstimo não encontrado"}

    emprestimo = emprestimos[dados.indice]

    if emprestimo["status"] != "aprovado":
        return {"erro": "Este empréstimo ainda não foi aprovado ou já foi pago"}

    # Cálculo simples do valor da parcela com juros
    valor = emprestimo['valor']
    taxa = emprestimo["taxa"]
    parcelas = dados.parcelas

    parcela_com_juros = valor * (1 + taxa) / parcelas

    emprestimo["status"] = "pago"
    emprestimo["parcelas"] = parcelas
    emprestimo["valor_total_pago"] = round(parcela_com_juros * parcelas, 2)
    emprestimo["valor_parcela"] = round(parcela_com_juros, 2)

    return {
        "msg": f"Empréstimo quitado em {parcelas} parcelas",
        "detalhes": emprestimo
    }

# Modelo para depósito em reais
class Deposito(BaseModel):
    nome: str
    valor: float

# Endpoint para depositar saldo em reais
@app.post("/depositar")
def depositar(dados: Deposito):
    usuario = next((u for u in usuarios if u["nome"] == dados.nome), None)
    if not usuario:
        return {"erro": "Usuário não encontrado"}

    if dados.valor <= 0:
        return {"erro": "O valor do depósito deve ser maior que zero"}

    usuario["saldo_reais"] += dados.valor

    return {
        "msg": f"Depósito de R${dados.valor} realizado com sucesso",
        "usuario": {
            "nome": usuario["nome"],
            "saldo_reais": usuario["saldo_reais"],
            "saldo_crypto": usuario["saldo_crypto"]
        }
    }

# Modelo para conversão de reais para cripto
class Conversao(BaseModel):
    nome: str
    valor: float

# Endpoint para converter reais em cripto (mockado)
@app.post("/converter")
def converter(dados: Conversao):
    usuario = next((u for u in usuarios if u["nome"] == dados.nome), None)
    if not usuario:
        return {"erro": "Usuário não encontrado"}

    if dados.valor <= 0:
        return {"erro": "O valor deve ser maior que zero"}

    if usuario["saldo_reais"] < dados.valor:
        return {"erro": "Saldo insuficiente em reais"}

    # Conversão simulada com cotação fixa
    cotacao = 0.00003
    convertido = dados.valor * cotacao

    usuario["saldo_reais"] -= dados.valor
    usuario["saldo_crypto"] += convertido

    return {
        "msg": f"Conversão realizada: R${dados.valor} → {convertido:.2f} BTC",
        "usuario": {
            "nome": usuario["nome"],
            "saldo_reais": usuario["saldo_reais"],
            "saldo_crypto": usuario["saldo_crypto"]
        }
    }
