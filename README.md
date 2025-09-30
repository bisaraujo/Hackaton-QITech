# Plataforma de Empréstimos P2P com Carteira Digital Cripto

Este repositório contém o protótipo inicial desenvolvido para o Hackathon QI Tech 2025.  
A aplicação é uma API em Python (FastAPI) que simula um sistema de empréstimos P2P integrado a uma carteira digital com saldo em Reais e Cripto.

## Funcionalidades já implementadas
- Cadastro de usuários com cálculo automático de score de crédito.
- Consulta de usuários cadastrados.
- Depósito em reais na carteira digital.
- Conversão de reais para cripto (mock com cotação fixa).
- Solicitação de empréstimo com taxa definida pelo score.
- Aprovação de empréstimos por investidores.
- Simulação de pagamento de parcelas com cálculo de juros.

## Estrutura do projeto
- `main.py` → contém todas as rotas e lógica de negócio.
- Dados armazenados em listas em memória (mock para o MVP).  
  Futuramente o sistema poderá ser conectado a SQLite ou PostgreSQL.

## Tecnologias utilizadas
- Python 3.10+  
- FastAPI  
- Uvicorn  
- Pydantic  

## Como rodar o projeto localmente

1. Clone o repositório:
   ```bash
   git clone https://github.com/bisaraujo/Hackaton-QITech.git

2. Crie e ative um ambiente virtual:
```bash
   python -m venv venv
   source venv/bin/activate   # Linux/Mac
   venv\Scripts\activate      # Windows
```
3. Instale as dependências:
```bash
   pip install fastapi uvicorn pydantic

```
4. Rode o servidor:
```bash
   uvicorn main:app --reload

```
Acesse a documentação interativa:
```bash
   http://127.0.0.1:8000/docs
