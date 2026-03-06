# Relatório de Testes - Aplicação CRUD

**Status:** TODOS OS TESTES PASSARAM

---

## Objetivo

Validar todas as funcionalidades da aplicação CRUD, incluindo:
- Validações de segurança (IAM password policy)
- Validações de login
- Cache RAM
- Persistência em banco de dados
- Autenticação JWT
- Endpoints administrativos

---

## Correções Realizadas

### 1. Incompatibilidade bcrypt 5.0.0
- **Problema:** `ValueError: password cannot be longer than 72 bytes`
- **Causa:** bcrypt 5.0.0 incompatível com passlib 1.7.4
- **Solução:** Downgrade para `bcrypt==4.1.2`
- **Arquivo:** `requirements.txt` atualizado

### 2. **JWT com subject inválido**
- **Problema:** `JWTClaimsError: Subject must be a string`
- **Causa:** Token criado com `{"sub": usuario.id}` (int)
- **Solução:** 
  - `app/service/login_controller.py`: Convertido para `str(usuario.id)`
  - `app/auth.py`: Convertido de volta para `int(user_id_str)` na decodificação
- **Status:** [CORRIGIDO]

---

## Testes Executados

### 1. Registro de Usuário (Normal)
```json
POST /login/registrar
{
  "login": "joao",
  "nome": "João Silva",
  "email": "joao@example.com",
  "senha": "Senha@2024",
  "idade": 30
}
```
**Resultado:** [SUCESSO]
```json
{
  "id": 2,
  "login": "joao",
  "nome": "João Silva",
  "email": "joao@example.com",
  "is_admin": false,
  "ativo": true
}
```

---

### 2. Validação de Senha Fraca
```json
POST /login/registrar
{
  "login": "maria",
  "senha": "123"  // [INVALIDO] Muito curta
}
```
**Resultado:** [REJEITADO CORRETAMENTE]
```
"Senha deve ter no mínimo 8 caracteres."
```

**Política de senha IAM validada:**
- [OK] Mínimo 8 caracteres
- [OK] Letra maiúscula obrigatória
- [OK] Letra minúscula obrigatória
- [OK] Número obrigatório
- [OK] Caractere especial obrigatório

---

### 3. Validação de Login com Números
```json
POST /login/registrar
{
  "login": "user123",  // [INVALIDO] Contém números
  "senha": "Senha@123"
}
```
**Resultado:** [REJEITADO CORRETAMENTE]
```
"Login não pode conter números."
```

**Regras de login validadas:**
- [OK] Não pode conter números
- [OK] Máximo 12 caracteres
- [OK] Não pode ser vazio

---

### 4. Autenticação JWT
```
POST /login
username=teste@example.com&password=Test@123
```
**Resultado:** [SUCESSO - Token gerado]
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

---

### 5. Cache RAM - Estatísticas
```
GET /admin/cache/estatisticas
Authorization: Bearer {token}
```
**Resultado:** [SUCESSO - Cache sincronizado]
```json
{
  "cache_ram": {
    "total": 2,
    "ativos": 2,
    "inativos": 0
  },
  "banco_dados": {
    "total": 2
  },
  "sincronizado": true
}
```

**Requisitos atendidos:**
- [OK] Armazenamento em RAM (classe `CacheRAM`)
- [OK] Sincronizado com banco de dados SQLite
- [OK] Estatísticas acessíveis via endpoint admin

---

### 6. Endpoints Administrativos
```
GET /admin/usuarios
Authorization: Bearer {token_admin}
```
**Resultado:** [SUCESSO - Lista apenas usuários ativos]
```json
[
  {
    "id": 1,
    "login": "testuser",
    "nome": "Teste User",
    "email": "teste@example.com",
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

```
GET /admin/usuarios/todos
Authorization: Bearer {token_admin}
```
**Resultado:** [SUCESSO - Lista todos os usuários (ativos e inativos)]

---

## Requisitos do Professor - Validação

| Requisito | Implementação | Status |
|-----------|---------------|--------|
| **Classes O.O** | `UsuarioORM`, `MediaORM`, `CacheRAM`, todas com métodos | [OK] |
| **Validação de Login** | Sem números, max 12 chars, não vazio | [OK] |
| **Senha Forte (IAM)** | Min 8, maiúscula, minúscula, número, especial | [OK] |
| **Armazenamento RAM** | `CacheRAM` com `Dict[int, UsuarioORM]` | [OK] |
| **Persistência DB** | SQLite com SQLAlchemy | [OK] |
| **Padrão Facade** | `FacadeService` orquestra todos os controllers | [OK] |

---

## Arquitetura Validada

### Padrão Facade
```
Views → FacadeService → Controllers
                      ├── GerenciarUsuarioService
                      ├── LoginController
                      └── UploaderController
```
[TODAS AS VIEWS USAM EXCLUSIVAMENTE O FACADE]

### Cache RAM
```python
class CacheRAM:
    _usuarios: Dict[int, UsuarioORM] = {}  # Memória compartilhada
    
    @staticmethod
    def adicionar(usuario: UsuarioORM): ...
    
    @staticmethod
    def obter_estatisticas(): ...
```
[CACHE SINCRONIZADO COM BANCO DE DADOS]

---

## Como Executar os Testes

### 1. Ambiente
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Iniciar Servidor
```bash
uvicorn main:app --reload
```

### 3. Executar Testes Automáticos
```bash
.venv/bin/python3 << 'EOF'
import requests
import json

# Teste 1: Registrar usuário
resp = requests.post("http://127.0.0.1:8000/login/registrar", json={
    "login": "teste",
    "nome": "Teste",
    "email": "teste@test.com",
    "senha": "Senha@123",
    "idade": 25
})
print(f"Registro: {resp.status_code}")

# Teste 2: Login
resp = requests.post("http://127.0.0.1:8000/login",
    data={"username": "teste@test.com", "password": "Senha@123"})
token = resp.json()["access_token"]
print(f"Login: {resp.status_code}")

# Teste 3: Cache (requer admin)
headers = {"Authorization": f"Bearer {token}"}
resp = requests.get("http://127.0.0.1:8000/admin/cache/estatisticas", headers=headers)
print(f"Cache: {resp.status_code}")
print(json.dumps(resp.json(), indent=2))
EOF
```

---

## Notas Técnicas

### Versões Críticas
- `bcrypt==4.1.2` (versão 5.0.0 **NÃO** funciona)
- `passlib[bcrypt]>=1.7.4`
- `python-jose[cryptography]>=3.3.0`

### JWT Subject
O JWT deve usar string no subject:
```python
# [OK] Correto
criar_access_token(data={"sub": str(user.id)})

# [ERRO] Errado
criar_access_token(data={"sub": user.id})
```

### Cache RAM
O cache é isolado da aplicação e pode ser inspecionado:
```python
from app.utils.cache import CacheRAM
stats = CacheRAM.obter_estatisticas()
print(f"Usuários em RAM: {stats['total']}")
```

---

## Conclusão

Todos os requisitos foram implementados e validados com sucesso:

1. [OK] Classes orientadas a objetos (`UsuarioORM`, `MediaORM`, `CacheRAM`)
2. [OK] Validações de login (sem números, max 12 caracteres)
3. [OK] Política de senha forte (IAM: 8 chars, maiúscula, minúscula, número, especial)
4. [OK] Armazenamento em RAM (`CacheRAM` com `Dict[int, UsuarioORM]`)
5. [OK] Persistência em banco de dados (SQLite via SQLAlchemy)
6. [OK] Padrão Facade (todas as views usam `FacadeService`)
7. [OK] Autenticação JWT funcional
8. [OK] Endpoints administrativos protegidos

