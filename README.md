# Crud_MSoftware

> Projeto acadêmico de **Métodos de Projetos de Software** demonstrando a aplicação de padrões de projeto em uma API REST.

## Descrição

API REST desenvolvida com FastAPI que implementa um sistema de gerenciamento de usuários e mídias, aplicando os padrões de projeto **Facade** e **MVC**

### Funcionalidades

- **Usuários**: Cadastro, autenticação JWT, edição de perfil próprio
- **Administradores**: Gerenciamento completo de usuários e permissões
- **Mídias**: Upload, listagem e exclusão de arquivos (imagens, vídeos, áudios, PDFs)

## Padrões de Projeto Aplicados

### 1. Facade Pattern [IMPLEMENTADO]
- `FacadeService`: Ponto único de acesso das views para os serviços
- Simplifica a interação entre camadas
- Encapsula a complexidade dos controllers
- **Localização**: [app/service/facade_service.py](app/service/facade_service.py)

### 2. MVC (Model-View-Controller) [IMPLEMENTADO]
- **Models** (`app/models/`): Entidades ORM e schemas Pydantic
  - `UsuarioORM`: Classe de entidade com métodos de negócio
  - `MediaORM`: Classe de entidade para mídias
- **Views** (`app/views/`): Rotas e endpoints da API (routers)
- **Controllers** (`app/service/`): Lógica de negócio
  - `LoginController`: Autenticação e perfil próprio
  - `GerenciarUsuarioService`: CRUD administrativo
  - `UploaderController`: Upload de mídias

### 3. Orientação a Objetos [IMPLEMENTADO]
- **Classes principais**:
  - `UsuarioORM`: Entidade com métodos `atualizar_dados()`, `desativar()`
  - `AdministradorMixin`: Comportamentos administrativos
  - `GerenciarUsuarioService`: Serviço de gerenciamento
  - `LoginController`: Controlador de autenticação
  - `UploaderController`: Controlador de upload
  - `FacadeService`: Fachada orquestradora
  - `CacheRAM`: Utilitário de cache em memória
- **Pacotes organizados** por responsabilidade: models, views, service, utils

## Tecnologias

- **FastAPI** - Framework web moderno e rápido
- **SQLAlchemy** - ORM para banco de dados
- **SQLite** - Banco de dados relacional
- **JWT** - Autenticação stateless
- **Pydantic** - Validação de dados
- **Uvicorn** - Servidor ASGI

## Estrutura do Projeto

```
Crud_MSoftware/
├── app/
│   ├── models/          # Modelos ORM e schemas
│   │   ├── usuario.py
│   │   └── media.py
│   ├── views/           # Endpoints da API (routers)
│   │   ├── login.py
│   │   ├── usuarios.py
│   │   └── medias.py
│   ├── service/         # Lógica de negócio
│   │   ├── facade_service.py      # <<Facade>>
│   │   ├── login_controller.py
│   │   ├── gerenciar_usuario.py
│   │   └── uploader_controller.py
│   ├── auth.py          # Autenticação JWT
│   └── database.py      # Configuração do banco
├── uploads/             # Arquivos enviados pelos usuários
├── main.py              # Aplicação FastAPI
├── .env                 # Variáveis de ambiente
└── requirements.txt     # Dependências
```

## Como Rodar

### 1. Clonar o repositório

```bash
git clone <url-do-repositorio>
cd Crud_MSoftware
```

### 2. Criar e ativar ambiente virtual

```bash
python3 -m venv .venv
source .venv/bin/activate  # Linux/Mac
# ou
.venv\Scripts\activate  # Windows
```

### 3. Instalar dependências

```bash
pip install -r requirements.txt
```

### 4. Configurar variáveis de ambiente

Crie o arquivo `.env` na raiz do projeto (ou use o existente):

```env
# JWT
SECRET_KEY=MUDE_ESTA_CHAVE_SECRETA_EM_PRODUCAO
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60

# Banco de dados
DATABASE_URL=sqlite:///./crud_msoftware.db
```

**NOTA DE SEGURANÇA**: Este arquivo contém valores de exemplo seguros para ambiente acadêmico/desenvolvimento.
Em produção real, substitua `SECRET_KEY` por uma chave criptograficamente segura e adicione `.env` ao `.gitignore`.

### 5. Criar pasta de uploads

```bash
mkdir uploads
```

### 6. Rodar o servidor

```bash
uvicorn main:app --reload
```

O servidor estará disponível em:
- **API**: http://127.0.0.1:8000
- **Documentação interativa**: http://127.0.0.1:8000/docs
- **Documentação alternativa**: http://127.0.0.1:8000/redoc

## Endpoints Principais

### Onde adicionar usuário (2 formas):
1. **Cadastro público**: `POST /login/registrar` 
   - Qualquer pessoa pode se registrar
   - Sempre cria usuário comum (não-admin)
   - **Código**: [app/views/login.py](app/views/login.py) → `LoginController.registrar()`

2. **Cadastro administrativo**: `POST /admin/usuarios`
   - Apenas administradores
   - Pode criar usuário comum ou admin
   - **Código**: [app/views/usuarios.py](app/views/usuarios.py) → `GerenciarUsuarioService.cadastro()`

### Onde listar todos os usuários:
- **Endpoint**: `GET /admin/usuarios/todos`
- **Código**: [app/views/usuarios.py](app/views/usuarios.py) → `GerenciarUsuarioService.visualizar_todos_usuarios()`
- **Acesso**: Apenas administradores
- **Retorna**: Todos os usuários (ativos + inativos)

### Onde ver cache em RAM:
- **Endpoint**: `GET /admin/cache/estatisticas`
- **Código**: [app/views/usuarios.py](app/views/usuarios.py) → `CacheRAM.obter_estatisticas()`
- **Demonstra**: Dupla camada de armazenamento (RAM + BD)

---

### Autenticação
- `POST /login` - Autenticar usuário
- `POST /registrar` - Registrar novo usuário

### Usuários (Requer autenticação)
- `GET /perfil` - Ver perfil próprio
- `PUT /perfil` - Editar perfil próprio
- `DELETE /perfil` - Encerrar conta

### Administração (Requer permissão admin)
- `GET /admin/usuarios` - Listar usuários ativos
- `GET /admin/usuarios/todos` - Listar todos os usuários
- `POST /admin/usuarios` - Criar novo usuário
- `PUT /admin/usuarios/{id}` - Editar usuário
- `DELETE /admin/usuarios/{id}` - Deletar usuário
- `PATCH /admin/usuarios/{id}/permissoes` - Alterar permissões

### Mídias (Requer autenticação)
- `POST /medias` - Upload de mídia
- `GET /medias` - Listar minhas mídias
- `DELETE /medias/{id}` - Deletar mídia própria

## Diagramas

Os diagramas de arquitetura e casos de uso estão disponíveis abaixo:

https://www.canva.com/design/DAG7KDuzUMA/cgGiGQBSA8fwyYIMTHsvQw/edit

---

## Descrição de Casos de Uso

https://docs.google.com/document/d/1fdJ6l94bLIARBVS7ogIy57HU73l-4crGGptiMkxgb_k/edit?usp=sharing

---
## Documento de Requisitos

https://docs.google.com/document/d/1s_cEoT9iPPbcc_5mt7ZMdjlJKvozlz91v9zGBvFSz14/edit?usp=sharing

---
## Diagrama de Casos de Uso
https://lucid.app/lucidchart/670aa4b8-6897-436b-b60b-5da51f1eb05a/edit?viewport_loc=-4532%2C-144%2C3924%2C2336%2C0_0&invitationId=inv_9f878370-8be6-4de3-869e-3d9dd72b3e7c

---
## Evidências de Implementação

### Para o Professor: Onde Encontrar Cada Requisito

| Requisito | Status | Localização no Código |
|-----------|--------|----------------------|
| **Orientação a Objetos (classes)** | [OK] | Classes em `app/models/`, `app/service/`, `app/utils/` |
| **Adicionar usuário** | [OK] | `POST /login/registrar` e `POST /admin/usuarios` |
| **Listar todos os usuários** | [OK] | `GET /admin/usuarios/todos` |
| **Armazenamento em RAM** | [OK] | `CacheRAM._usuarios` em [app/utils/cache.py](app/utils/cache.py#L17) |
| **Validação login (12 chars)** | [OK] | [app/models/usuario.py](app/models/usuario.py#L84-L94) - `login_valido()` |
| **Validação login (não vazio)** | [OK] | [app/models/usuario.py](app/models/usuario.py#L84-L94) - `login_valido()` |
| **Validação login (sem números)** | [OK] | [app/models/usuario.py](app/models/usuario.py#L84-L94) - `login_valido()` |
| **Política de senha IAM** | [OK] | [app/models/usuario.py](app/models/usuario.py#L96-L119) - `senha_forte()` |
| **Persistência em BD** | [OK] | SQLite configurado em [app/database.py](app/database.py) |
| **Padrão Facade** | [OK] | [app/service/facade_service.py](app/service/facade_service.py) |
| **Padrão MVC** | [OK] | Models: `app/models/`, Views: `app/views/`, Controllers: `app/service/` |

### Testando o Cache em RAM

Após rodar o servidor e criar alguns usuários, acesse:
```
GET http://127.0.0.1:8000/admin/cache/estatisticas
```

Exemplo de resposta:
```json
{
  "cache_ram": {
    "total": 5,
    "ativos": 4,
    "inativos": 1
  },
  "banco_dados": {
    "total": 5
  },
  "sincronizado": true
}
```

---

## Segurança

### Validações de Login [IMPLEMENTADO]
Todas implementadas em [app/models/usuario.py](app/models/usuario.py):
- **Não vazio**: Login não pode ser vazio ou apenas espaços em branco
- **Máximo 12 caracteres**: Limite de tamanho do login
- **Sem números**: Login não pode conter dígitos numéricos

### Política de Senha Forte (estilo IAM/AWS) [IMPLEMENTADO]
Implementada em [app/models/usuario.py](app/models/usuario.py):
- **Mínimo 8 caracteres**
- **Pelo menos 1 letra maiúscula**
- **Pelo menos 1 letra minúscula**
- **Pelo menos 1 número**
- **Pelo menos 1 caractere especial** (!@#$%^&*()_+-=[]{}|;:,.<>?/~`)

### Outras Medidas de Segurança
- Senhas hasheadas com **bcrypt**
- Tokens **JWT** para autenticação stateless
- Validação de tipos **MIME** para uploads
- Controle de permissões por **role** (usuário/admin)

## Armazenamento de Dados

### 1. Cache em RAM [IMPLEMENTADO]
- **Classe**: `CacheRAM` ([app/utils/cache.py](app/utils/cache.py))
- **Estrutura**: Dicionário Python `Dict[int, UsuarioORM]`
- **Finalidade**: Acesso rápido aos dados sem consultar o banco
- **Sincronização**: Automática entre RAM e BD em todas as operações (criar, atualizar, deletar)
- **Endpoint de demonstração**: `GET /admin/cache/estatisticas`

### 2. Persistência em SQLite [IMPLEMENTADO]
- **Arquivo**: `crud_msoftware.db` (criado automaticamente)
- **ORM**: SQLAlchemy
- **Configuração**: [app/database.py](app/database.py)
- **Dupla camada**: Dados sempre salvos em RAM **E** BD simultaneamente

## Implementações Concluídas

- [x] **Padrão Facade** completo
- [x] **Padrão Repository** com cache em RAM
- [x] **Padrão MVC** estruturado
- [x] **Orientação a Objetos** com classes e pacotes organizados
- [x] **Validações de login** (12 chars, não vazio, sem números)
- [x] **Política de senha forte** estilo IAM/AWS
- [x] **Armazenamento em RAM** (cache sincronizado)
- [x] **Persistência em SQLite** com SQLAlchemy
- [x] **Autenticação JWT**
- [x] **Upload de mídias** com validação de tipo

