# RigTech

Plataforma de gestão agrícola desenvolvida como projeto acadêmico na disciplina de **Métodos e Projeto de Software** da UFPB. O sistema oferece ferramentas para o gerenciamento de talhões de cana-de-açúcar, análise de imagens de satélite via índice NDVI, upload de imagens de drone e registro de notas operacionais — tudo integrado em uma interface desktop e uma API REST.

---

## Funcionalidades

### Autenticação
- Cadastro de usuários com validação de login (máx. 12 caracteres, sem números) e senha forte (mín. 8 caracteres, letras maiúsculas, minúsculas, números e caractere especial)
- Login com verificação de hash seguro
- Perfil de administrador com acesso a estatísticas e listagem de usuários

### Notas
- Criação, edição e exclusão de notas
- Upload de anexos (PDF, imagens, GeoTIFF, Shapefile, entre outros)
- Histórico de edições com timestamps
- Desfazer (undo) de operações via padrão Memento
- Exportação de notas em **PDF** ou **TXT**

### Talhões
- Cadastro de talhões com variedade de cana, tipo de solo, idade, status e previsão de colheita
- Status disponíveis: `Ativo`, `Em colheita`, `Pousio`, `Replantio`
- Edição e remoção de talhões
- Upload de imagens de drone (GeoTIFF) vinculadas ao talhão
- Visualização das imagens de drone cadastradas por talhão

### Imagens de Satélite (Sentinel-2 / Copernicus)
- Busca de imagens disponíveis para uma área geográfica e período definidos
- Cálculo do índice **NDVI** (Normalized Difference Vegetation Index) e **EVI**
- Detecção automática de anomalias na vegetação classificadas por severidade:
  - `BAIXA` — NDVI entre 0,2 e 0,3
  - `MÉDIA` — NDVI entre 0,1 e 0,2
  - `ALTA` — NDVI abaixo de 0,1
- Requer credenciais do [Copernicus Data Space](https://dataspace.copernicus.eu)

---

## Instalação

### Pré-requisitos
- Python 3.10 ou superior
- Tkinter (geralmente incluído no Python; se não estiver):
  ```bash
  # Ubuntu/Debian
  sudo apt install python3-tk

  # Fedora/RHEL
  sudo dnf install python3-tkinter
  ```

### Passos

```bash
# 1. Clone o repositório
git clone <url-do-repositorio>
cd Crud_MSoftware

# 2. Crie e ative o ambiente virtual
python -m venv .venv

# Windows
.venv\Scripts\activate

# Linux/macOS
source .venv/bin/activate

# 3. Instale as dependências
pip install -r requirements.txt
```

---

## Como executar

```bash
python main.py
```

Por padrão o sistema abre a **interface gráfica (GUI)**. As configurações de execução ficam no topo do arquivo `main.py`:

```python
ACTIVE_STORAGE   = "json"    # "json" para persistir em arquivo | "mem" para memória (sem persistência)
ACTIVE_LOGGER    = "console" # "console" para terminal          | "file" para gravar em logs/app.log
ACTIVE_INTERFACE = "gui"     # "gui" para interface desktop     | "api" para API REST
```

---

## Interface Gráfica (GUI)

A GUI é organizada em uma barra lateral com os módulos do sistema. Após fazer login, o usuário tem acesso a:

### Notas
Painel de criação e gerenciamento de notas textuais.

- **Nova nota** — abre um formulário com título e conteúdo
- **Editar** — altera o conteúdo de uma nota existente
- **Excluir** — remove a nota com confirmação
- **Desfazer** — reverte a última operação (criar, editar, excluir ou anexar)
- **Histórico** — exibe os snapshots anteriores da nota com timestamps
- **Anexar arquivo** — vincula um arquivo à nota (PDF, imagem, GeoTIFF, ZIP, etc.)
- **Exportar** — gera um arquivo PDF ou TXT com o conteúdo da nota

### Talhões
Painel de cadastro e monitoramento de parcelas de terra.

- **Novo talhão** — formulário com nome, variedade de cana, tipo de solo, idade, status, irrigação e datas de colheita
- **Editar / Remover** — gerenciamento do cadastro existente
- **Detalhe do talhão** — exibe todas as informações e as imagens de drone vinculadas
- **Upload de imagem de drone** — seleciona um arquivo GeoTIFF (`.tif`/`.tiff`) e o vincula ao talhão; o arquivo é salvo em `data/drone_images/`

### Upload de Drone
Painel dedicado ao envio de imagens georreferenciadas independente de talhão, com seleção de arquivo e confirmação de envio.

### Imagens de Satélite
Painel de análise remota via API do Copernicus.

1. Informe as **credenciais do Copernicus** (usuário e senha)
2. Defina a **área de busca** (bounding box: lat/lon mínimos e máximos)
3. Defina o **período** e o limite de cobertura de nuvens
4. Clique em **Buscar imagens** — a lista de imagens disponíveis será carregada
5. Selecione uma imagem e clique em **Calcular NDVI** (ou EVI)
6. Clique em **Detectar anomalias** para identificar regiões com vegetação comprometida
7. As anomalias são exibidas com coordenadas e nível de severidade

---

## API REST

Para usar a API em vez da GUI, altere `ACTIVE_INTERFACE = "api"` em `main.py` e execute:

```bash
python main.py
```

A documentação interativa estará disponível em:

```
http://127.0.0.1:8000/docs
```

### Grupos de endpoints disponíveis

| Grupo | Endpoints |
|---|---|
| **Auth** | `POST /register`, `POST /login` |
| **Notes** | CRUD completo, anexos, histórico, undo, exportação PDF/TXT |
| **Talhoes** | CRUD completo |
| **Satelite** | Busca, processamento NDVI/EVI, detecção de anomalias |
| **Admin** | Estatísticas de uso, listagem de usuários |

---

## Arquitetura e Padrões de Projeto

O projeto aplica **10 padrões GOF** documentados em [`PADROES_GOF.md`](PADROES_GOF.md):

| Padrão | Categoria | Onde é aplicado |
|---|---|---|
| Factory Method | Criacional | `CommandFactory` — centraliza a criação de todos os comandos do sistema |
| Prototype | Criacional | `Note.clone()` — cópia profunda usada pelo Memento antes de edições e exclusões |
| Adapter | Estrutural | `LoggerAdapter` — abstrai destinos de log (console ou arquivo) usados por todos os serviços |
| Bridge | Estrutural | `NoteRepository`, `UserRepository`, `TalhaoRepository` + `StorageStrategy` — separa repositórios da implementação de persistência |
| Chain of Responsibility | Comportamental | Validação de anexos em notas e talhões (`ContentValidator → SizeValidator → FormatValidator`) |
| Command | Comportamental | Todas as operações de nota (criar, editar, excluir, anexar) encapsuladas com suporte a undo |
| Memento | Comportamental | `NoteCaretaker` preserva histórico de estados de notas para desfazer operações |
| Observer | Comportamental | `NoteEventBus` notifica eventos de notas (log, estatísticas); `SatelliteEventBus` notifica buscas, cálculos NDVI e anomalias detectadas |
| Strategy | Comportamental | Troca de armazenamento (JSON/memória) em todos os repositórios; troca de interface (GUI/API REST) no bootstrap |
| Template Method | Comportamental | `NoteExporter` define o esqueleto de exportação reutilizado por `PdfNoteExporter` e `PlainTextNoteExporter` |

---

## Testes

```bash
python -m pytest tests/ -v
```

A suíte cobre autenticação, modelos, repositórios, serviços, padrões GOF e endpoints da API REST — **150 testes** no total.

---

## Estrutura do projeto

```
app/
├── interface/       # GUI Tkinter e API FastAPI
├── models/          # Entidades: Note, Usuario, Talhao, Satellite
├── patterns/        # Padrões GOF: Command, Memento, Observer, Chain, Factory, Export
├── repository/      # Repositórios e estratégias de armazenamento
├── services/        # Regras de negócio
└── utils/           # Logger Adapter e cliente Copernicus
data/                # Arquivos JSON de persistência e imagens de satélite
logs/                # Log da aplicação
uploads/             # Anexos das notas
tests/               # Testes automatizados
```
