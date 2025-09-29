from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class User(BaseModel):
    nome: str
    renda: float
    dividas: int = 0
    
usuarios = []

def calcula_score(renda, dividas):
    score = (renda/ (dividas + 1)) * 10
    return max(300, min(900, int(score)))

@app.post("/cadastro")
def cadastro(user: User):
    score = calcula_score(user.renda, user.dividas)
    usuario = user.dict()
    usuario["score"] = score
    usuario["saldo_reais"] = 0.0
    usuario["saldo_crypto"] = 0.0
    usuarios.append(usuario)
    return {"msg": f"Usuario {user.nome} cadastrado com sucesso!", "data":usuario}

@app.get("/usuarios")
def listar_usuarios():
        return {"usuarios": usuarios}
    
class Emprestimo(BaseModel):
    nome: str
    valor:float

emprestimos = []

@app.post("/emprestimo")
def solicitar_emprestimo(pedido: Emprestimo):
    usuario = next((u for u in usuarios if u["nome"] == pedido.nome), None)
    if not usuario:
        return {'erro':"Usuário não encontrado!"}
    
    score = usuario["score"]
    if score >= 700:
        taxa = 0.02
    elif score >= 500:
        taxa = 0.05
    else:
        taxa = 0.1
        
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
    
@app.get("/emprestimos")
def listar_emprestimos():
    return {"emprestimos": emprestimos}

class AprovarEmprestimo(BaseModel):
    indice: int
    investidor: str
    
@app.post("/aprovar")
def aprovar_emprestimo(dados: AprovarEmprestimo):
    if dados.indice < 0 or dados.indice >= len(emprestimos):
        return {"erro": "Empréstimo não encontrado"}
    
    emprestimo = emprestimos[dados.indice]
    
    if emprestimo["status"] != "aguardando investidor":
        return {"erro": "Este empréstimo já foi processado"}
    
    emprestimo["status"] = "aprovado"
    emprestimo["investidor"] = dados.investidor
    
    return {
        "msg": f"Empréstimo aprovado por {dados.investidor}",
        "emprestimo": emprestimo
    }
    
class Pagamento(BaseModel):
    indice: int
    parcelas: int
    
@app.post("/pagar")
def pagar_emprestimo(dados: Pagamento):
    if dados.indice < 0 or dados.indice >= len(emprestimos):
        return {"erro": "Empréstimo não encontrado"}
    
    emprestimo = emprestimos[dados.indice]
    
    if emprestimo["status"] != "aprovado":
        return {"erro": "Este empréstimo ainda não foi aprovado ou já foi pago"}
    
    valor = emprestimo['valor']
    taxa = emprestimo["taxa"]
    parcelas = dados.parcelas
    
    parcela_com_juros = valor * (1 + taxa)/parcelas
    
    emprestimo["status"] = "pago"
    emprestimo["parcelas"] = parcelas
    emprestimo["valor_total_pago"] = round(parcela_com_juros * parcelas, 2)
    emprestimo["valor_parcela"] = round(parcela_com_juros, 2)
    
    return {
        "msg": f"Empréstimo quitado em {parcelas} parcelas",
        "detalhes": emprestimo
    }

class Deposito(BaseModel):
    nome: str
    valor: float

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
    
class Conversao(BaseModel):
    nome:str
    valor: float
    
@app.post("/converter")
def converter(dados: Conversao):
    usuario = next((u for u in usuarios if u["nome"] == dados.nome), None)
    if not usuario:
        return {"erro": "Usuário não encontrado"}
    
    if dados.valor <= 0:
        return {"erro": "O valor ddeve ser maior que zero"}
    
    if usuario["saldo_reais"] < dados.valor:
        return {"erro":"Saldo insuficiente em reais"}
    
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
    
    