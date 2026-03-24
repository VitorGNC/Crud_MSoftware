## Notes App com Design Patterns

Aplicacao desktop em Tkinter que demonstra varios design patterns ao mesmo tempo:

- Command + Sender/Invoker: a interface grafica dispara comandos que encapsulam cada acao do usuario.
- Memento: cada alteracao de nota gera um snapshot para desfazer e visualizar historico.
- Repository + Strategy: o armazenamento das notas troca em tempo real entre memoria RAM e arquivo JSON.
- Adapter: logs sao enviados para console e arquivo atraves de adaptadores.
- Interface Strategy: escolha entre GUI Tkinter e API FastAPI (Swagger) ajustando `ACTIVE_INTERFACE` em [main.py](main.py).

O gerenciamento de usuarios continua existindo (cadastro e login), agora alinhado ao dominio de notas.

## Principais diretorios

```
app/
├── interface/             # Camada de view (Tkinter)
├── models/                # Entidades Usuario e Note
├── patterns/              # Command, Memento, Receiver, Sender
├── repository/            # Repository + strategies (JSON / RAM)
├── services/              # Regras de negocio de usuarios e notas
└── utils/                 # Adapter para logs
data/                      # Persistencia em JSON
logs/                      # Arquivo de log
uploads/                   # Anexos das notas
```

## Como executar

```bash
python3 -m venv .venv
source .venv/bin/activate  # Windows use .venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

dependencies 

Fedora/RHEL/CentOS: sudo dnf install python3-tkinter


Ubuntu/Debian: sudo apt install python3-tk

## Fluxo de arquitetura

1. Uma `InterfaceStrategy` ([app/interface/interface_strategy.py](app/interface/interface_strategy.py)) decide entre GUI Tkinter e API FastAPI.
2. Na GUI, `NotesAppGUI` atua como **Sender** e transforma cliques em comandos; na API, os endpoints criam os mesmos comandos antes de despachá-los.
3. Os comandos sao executados pelo **CommandInvoker** ([app/patterns/command.py](app/patterns/command.py)), que guarda mementos no `NoteCaretaker`.
4. O **Receiver** ([app/patterns/receiver.py](app/patterns/receiver.py)) delega as operacoes para `NoteService`.
5. `NoteService` usa `NoteRepository` ([app/repository/note_repository.py](app/repository/note_repository.py)) que aplica o padrao Repository + Strategy.
6. `UserService` trabalha com `UserRepository` ([app/repository/user_repository.py](app/repository/user_repository.py)) usando a mesma estrategia configurada no bootstrap.
7. Logs trafegam pelo adapter em [app/utils/logger_adapter.py](app/utils/logger_adapter.py), configurado no bootstrap para enviar ao console ou ao arquivo `logs/app.log`.

## Papeis dos design patterns

- **Command**: `CreateNoteCommand`, `UpdateNoteCommand`, `AttachFileCommand`, `AttachContentCommand` e `DeleteNoteCommand`. Cada um encapsula parametros, sabe quando criar snapshots e como desfazer.
- **Memento**: `NoteMemento` e `NoteCaretaker` ([app/patterns/memento.py](app/patterns/memento.py)) armazenam historico de estados por nota.
- **Repository + Strategy**: `NoteRepository` e `UserRepository` aplicam as estrategias `JsonStorageStrategy` e `InMemoryStorageStrategy` ([app/repository/strategies.py](app/repository/strategies.py)), selecionadas no bootstrap via `ACTIVE_STORAGE`.
- **Adapter**: `LoggerAdapter` isola diferentes destinos de log (console e arquivo), mantendo interface unica para todos os serviços.
- **Interface Strategy**: `GuiInterfaceStrategy` e `RestApiInterfaceStrategy` ([app/interface/interface_strategy.py](app/interface/interface_strategy.py)) alternam entre a GUI e a API FastAPI com Swagger.

## Funcionalidades principais

- Cadastro e login com as mesmas regras do projeto original (validacao de login e senha forte em [app/models/usuario.py](app/models/usuario.py)).
- Criacao, edicao e exclusao de notas usando comandos.
- Visualizacao de historico (timestamps) e desfazer com Memento expostos tanto na GUI quanto na API.
- Anexo de arquivos armazenados na pasta `uploads/` com rastreabilidade no repositorio, inclusive via upload multipart (endpoint `/notes/{note_id}/attachments`).
- Troca de estrategia de persistencia (RAM ou JSON) alterando a constante `ACTIVE_STORAGE` em [main.py](main.py) e reiniciando o app.
- Troca de interface (GUI Tkinter ou API FastAPI com Swagger) mudando `ACTIVE_INTERFACE` antes de executar `python main.py`.

### Endpoints principais da API

- `POST /register` e `POST /login`: cadastro e autenticacao.
- `GET /notes`: lista notas do usuario autenticado.
- `POST /notes`, `PUT /notes/{note_id}`, `DELETE /notes/{note_id}`: CRUD completo reutilizando os comandos.
- `POST /notes/{note_id}/attachments`: upload multipart (`arquivo`) para anexar arquivos e sincronizar com `uploads/`.
- `GET /notes/{note_id}/history`: retorna o historico de mementos gravados pelo CommandInvoker.
- `POST /commands/undo`: desfaz a ultima operacao, replicando o botao **Desfazer** da GUI.

## Estrategia de log

- `ConsoleLogTarget` envia logs para o terminal.
- `FileLogTarget` grava o mesmo texto em `logs/app.log`.
- `LoggerAdapter` entrega metodos `info` e `error` consumidos pelos serviços; escolha o destino ativo ajustando `ACTIVE_LOGGER` em [main.py](main.py).

## Testes manuais sugeridos

1. Registrar um usuario novo, fazer login e criar notas com anexos.
2. Alterar `ACTIVE_INTERFACE` para `"api"`, rodar `python main.py` e testar os endpoints em http://127.0.0.1:8000/docs (Swagger).
3. Alterar `ACTIVE_STORAGE` para "mem" em [main.py](main.py), reiniciar o app e comparar o comportamento sem persistencia permanente em ambos os modos.
4. Editar uma nota varias vezes e usar **Desfazer** para restaurar cada estado.
5. Reabrir o app e conferir a leitura do arquivo `data/notes.json` e do historico exibido.

## Proximos passos possiveis

- Adicionar exportacao de nota em PDF usando Template Method.
- Expandir o Adapter de logs para integracoes remotas (HTTP, syslog etc).
- Criar testes automatizados para os comandos e para o caretaker.

