# Exemplos de Validação - Guia Prático

Este documento contém exemplos práticos de como testar todas as validações implementadas na aplicação.

---

## Pré-requisitos

1. Servidor rodando: `uvicorn main:app --reload`
2. Acesso à documentação interativa: http://127.0.0.1:8000/docs

---

## 1. Validações de Senha (Política IAM)

### Regras Implementadas
- Mínimo 8 caracteres
- Pelo menos 1 letra maiúscula
- Pelo menos 1 letra minúscula
- Pelo menos 1 número
- Pelo menos 1 caractere especial (!@#$%^&*()_+-=[]{}|;:,.<>?/~`)

### Exemplo: Senha VÁLIDA

```bash
curl -X POST http://127.0.0.1:8000/login/registrar \
  -H "Content-Type: application/json" \
  -d '{
    "login": "joao",
    "nome": "João Silva",
    "email": "joao@example.com",
    "senha": "Senha@2024",
    "idade": 30
  }'
```

**Resposta esperada (200 OK):**
```json
{
  "id": 1,
  "login": "joao",
  "nome": "João Silva",
  "email": "joao@example.com",
  "is_admin": false,
  "ativo": true
}
```

### Exemplo: Senha MUITO CURTA

```bash
curl -X POST http://127.0.0.1:8000/login/registrar \
  -H "Content-Type: application/json" \
  -d '{
    "login": "maria",
    "nome": "Maria",
    "email": "maria@example.com",
    "senha": "123",
    "idade": 25
  }'
```

**Resposta esperada (422 Unprocessable Entity):**
```json
{
  "detail": [
    {
      "type": "value_error",
      "loc": ["body", "senha"],
      "msg": "Value error, Senha deve ter no mínimo 8 caracteres."
    }
  ]
}
```

### Exemplo: Senha SEM MAIÚSCULA

```bash
curl -X POST http://127.0.0.1:8000/login/registrar \
  -H "Content-Type: application/json" \
  -d '{
    "login": "pedro",
    "nome": "Pedro",
    "email": "pedro@example.com",
    "senha": "senha@123",
    "idade": 28
  }'
```

**Resposta esperada (422):**
```json
{
  "detail": [
    {
      "type": "value_error",
      "loc": ["body", "senha"],
      "msg": "Value error, Senha deve conter pelo menos uma letra maiúscula."
    }
  ]
}
```

### Exemplo: Senha SEM NÚMERO

```bash
curl -X POST http://127.0.0.1:8000/login/registrar \
  -H "Content-Type: application/json" \
  -d '{
    "login": "ana",
    "nome": "Ana",
    "email": "ana@example.com",
    "senha": "SenhaForte@",
    "idade": 22
  }'
```

**Resposta esperada (422):**
```json
{
  "detail": [
    {
      "type": "value_error",
      "loc": ["body", "senha"],
      "msg": "Value error, Senha deve conter pelo menos um número."
    }
  ]
}
```

### Exemplo: Senha SEM CARACTERE ESPECIAL

```bash
curl -X POST http://127.0.0.1:8000/login/registrar \
  -H "Content-Type: application/json" \
  -d '{
    "login": "carlos",
    "nome": "Carlos",
    "email": "carlos@example.com",
    "senha": "Senha2024",
    "idade": 35
  }'
```

**Resposta esperada (422):**
```json
{
  "detail": [
    {
      "type": "value_error",
      "loc": ["body", "senha"],
      "msg": "Value error, Senha deve conter pelo menos um caractere especial."
    }
  ]
}
```

---

## 2. Validações de Login

### Regras Implementadas
- Não pode conter números
- Máximo 12 caracteres
- Não pode ser vazio

### Exemplo: Login COM NÚMEROS (INVÁLIDO)

```bash
curl -X POST http://127.0.0.1:8000/login/registrar \
  -H "Content-Type: application/json" \
  -d '{
    "login": "user123",
    "nome": "User Test",
    "email": "user@example.com",
    "senha": "Senha@123",
    "idade": 20
  }'
```

**Resposta esperada (422):**
```json
{
  "detail": [
    {
      "type": "value_error",
      "loc": ["body", "login"],
      "msg": "Value error, Login não pode conter números."
    }
  ]
}
```

### Exemplo: Login MAIOR QUE 12 CARACTERES (INVÁLIDO)

```bash
curl -X POST http://127.0.0.1:8000/login/registrar \
  -H "Content-Type: application/json" \
  -d '{
    "login": "usuariocomnomemuitolongo",
    "nome": "Usuario",
    "email": "usuario@example.com",
    "senha": "Senha@123",
    "idade": 27
  }'
```

**Resposta esperada (422):**
```json
{
  "detail": [
    {
      "type": "string_too_long",
      "loc": ["body", "login"],
      "msg": "String should have at most 12 characters"
    }
  ]
}
```

### Exemplo: Login VAZIO (INVÁLIDO)

```bash
curl -X POST http://127.0.0.1:8000/login/registrar \
  -H "Content-Type: application/json" \
  -d '{
    "login": "",
    "nome": "Usuario",
    "email": "usuario@example.com",
    "senha": "Senha@123",
    "idade": 27
  }'
```

**Resposta esperada (422):**
```json
{
  "detail": [
    {
      "type": "string_too_short",
      "loc": ["body", "login"],
      "msg": "String should have at least 1 character"
    }
  ]
}
```

---

## 3. Autenticação JWT

### Login com Credenciais Válidas

```bash
curl -X POST http://127.0.0.1:8000/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=joao@example.com&password=Senha@2024"
```

**Resposta esperada (200 OK):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwiZXhwIjoxNzA...",
  "token_type": "bearer"
}
```

### Login com Credenciais Inválidas

```bash
curl -X POST http://127.0.0.1:8000/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=joao@example.com&password=senhaerrada"
```

**Resposta esperada (401 Unauthorized):**
```json
{
  "detail": "Credenciais inválidas."
}
```

---

## 4. Cache RAM - Demonstração

### Obter Estatísticas do Cache (Requer Admin)

**Passo 1: Fazer login como admin**
```bash
TOKEN=$(curl -s -X POST http://127.0.0.1:8000/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin@example.com&password=Admin@123" \
  | python3 -c "import sys, json; print(json.load(sys.stdin)['access_token'])")
```

**Passo 2: Consultar estatísticas**
```bash
curl -X GET http://127.0.0.1:8000/admin/cache/estatisticas \
  -H "Authorization: Bearer $TOKEN"
```

**Resposta esperada (200 OK):**
```json
{
  "cache_ram": {
    "total": 3,
    "ativos": 3,
    "inativos": 0
  },
  "banco_dados": {
    "total": 3
  },
  "sincronizado": true
}
```

**Interpretação:**
- `cache_ram.total`: Quantidade de usuários armazenados na memória RAM
- `cache_ram.ativos`: Usuários ativos em RAM
- `banco_dados.total`: Quantidade de usuários no SQLite
- `sincronizado`: true se RAM e BD têm a mesma quantidade

---

## 5. Endpoints Administrativos

### Listar Todos os Usuários (Ativos + Inativos)

```bash
curl -X GET http://127.0.0.1:8000/admin/usuarios/todos \
  -H "Authorization: Bearer $TOKEN"
```

**Resposta esperada (200 OK):**
```json
[
  {
    "id": 1,
    "login": "admin",
    "nome": "Administrador",
    "email": "admin@example.com",
    "is_admin": true,
    "ativo": true
  },
  {
    "id": 2,
    "login": "joao",
    "nome": "João Silva",
    "email": "joao@example.com",
    "is_admin": false,
    "ativo": true
  }
]
```

### Listar Apenas Usuários Ativos

```bash
curl -X GET http://127.0.0.1:8000/admin/usuarios \
  -H "Authorization: Bearer $TOKEN"
```

**Resposta esperada (200 OK):**
```json
[
  {
    "id": 2,
    "login": "joao",
    "nome": "João Silva",
    "email": "joao@example.com",
    "is_admin": false,
    "ativo": true
  }
]
```

---

## 6. Teste Completo Automatizado

Salve este script como `test_validacoes.py` e execute com `.venv/bin/python3 test_validacoes.py`:

```python
import requests
import json

BASE_URL = "http://127.0.0.1:8000"

def test_senha_fraca():
    print("Teste: Senha Fraca")
    resp = requests.post(f"{BASE_URL}/login/registrar", json={
        "login": "teste",
        "nome": "Teste",
        "email": "teste@test.com",
        "senha": "123",
        "idade": 25
    })
    assert resp.status_code == 422
    print("  PASSOU: Senha fraca rejeitada")

def test_login_com_numeros():
    print("Teste: Login com Números")
    resp = requests.post(f"{BASE_URL}/login/registrar", json={
        "login": "user123",
        "nome": "User",
        "email": "user123@test.com",
        "senha": "Senha@123",
        "idade": 25
    })
    assert resp.status_code == 422
    print("  PASSOU: Login com números rejeitado")

def test_registro_valido():
    print("Teste: Registro Válido")
    resp = requests.post(f"{BASE_URL}/login/registrar", json={
        "login": "valido",
        "nome": "Usuário Válido",
        "email": "valido@test.com",
        "senha": "Senha@123",
        "idade": 30
    })
    assert resp.status_code == 200
    print("  PASSOU: Usuário criado com sucesso")

def test_login():
    print("Teste: Login")
    resp = requests.post(f"{BASE_URL}/login", data={
        "username": "valido@test.com",
        "password": "Senha@123"
    })
    assert resp.status_code == 200
    assert "access_token" in resp.json()
    print("  PASSOU: Login bem-sucedido")

if __name__ == "__main__":
    print("=== INICIANDO TESTES DE VALIDAÇÃO ===\n")
    test_senha_fraca()
    test_login_com_numeros()
    test_registro_valido()
    test_login()
    print("\n=== TODOS OS TESTES PASSARAM ===")
```

---

## 7. Usando a Documentação Interativa (Swagger)

Acesse http://127.0.0.1:8000/docs e experimente:

1. Clique em `POST /login/registrar`
2. Clique em "Try it out"
3. Teste os exemplos acima diretamente na interface
4. Observe as respostas de validação em tempo real

---

## Resumo das Validações

| Validação | Localização no Código | Testada |
|-----------|----------------------|---------|
| Senha: min 8 chars | app/models/usuario.py:111 | Sim |
| Senha: letra maiúscula | app/models/usuario.py:136-138 | Sim |
| Senha: letra minúscula | app/models/usuario.py:139-141 | Sim |
| Senha: número | app/models/usuario.py:142-144 | Sim |
| Senha: especial | app/models/usuario.py:145-147 | Sim |
| Login: sem números | app/models/usuario.py:126-128 | Sim |
| Login: max 12 chars | app/models/usuario.py:107 | Sim |
| Login: não vazio | app/models/usuario.py:108 | Sim |

---

## Notas Importantes

1. **Cache RAM**: O endpoint `/admin/cache/estatisticas` demonstra que os dados estão sendo armazenados em memória (RAM) e sincronizados com o banco de dados.

2. **Teste de Sincronização**: Crie um usuário, consulte o cache, reinicie o servidor e consulte novamente. O cache será recarregado do banco automaticamente.

3. **Persistência**: Todos os dados são salvos no arquivo `crud_msoftware.db` (SQLite) na raiz do projeto.

4. **Tokens JWT**: Os tokens têm validade de 60 minutos (configurável no .env).
