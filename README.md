## Notes App com Design Patterns

Aplicacao desktop em Tkinter que demonstra varios design patterns ao mesmo tempo:

- Command + Sender/Invoker: a interface grafica dispara comandos que encapsulam cada acao do usuario.
- Memento: cada alteracao de nota gera um snapshot para desfazer e visualizar historico.
- Repository + Strategy: o armazenamento das notas troca em tempo real entre memoria RAM e arquivo JSON.
- Adapter: logs sao enviados para console e arquivo atraves de adaptadores.

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

Nenhuma dependencia externa e necessaria, apenas a biblioteca padrao.

## Fluxo de arquitetura

1. A view (`NotesAppGUI`) atua como **Sender** e transforma cliques em comandos.
2. Os comandos sao executados pelo **CommandInvoker** ([app/patterns/command.py](app/patterns/command.py)), que guarda mementos no `NoteCaretaker`.
3. O **Receiver** ([app/patterns/receiver.py](app/patterns/receiver.py)) delega as operacoes para `NoteService`.
4. `NoteService` usa `NoteRepository` ([app/repository/note_repository.py](app/repository/note_repository.py)) que aplica o padrao Repository + Strategy.
5. Logs trafegam pelo adapter em [app/utils/logger_adapter.py](app/utils/logger_adapter.py) para console e arquivo `logs/app.log`.

## Papeis dos design patterns

- **Command**: `CreateNoteCommand`, `UpdateNoteCommand`, `AttachFileCommand` e `DeleteNoteCommand`. Cada um encapsula parametros, sabe quando criar snapshots e como desfazer.
- **Memento**: `NoteMemento` e `NoteCaretaker` ([app/patterns/memento.py](app/patterns/memento.py)) armazenam historico de estados por nota.
- **Repository + Strategy**: `NoteRepository` pode alternar entre `JsonStorageStrategy` e `InMemoryStorageStrategy` ([app/repository/strategies.py](app/repository/strategies.py)). A GUI permite trocar a estrategia durante a execucao.
- **Adapter**: `LoggerAdapter` isola diferentes destinos de log (console e arquivo), mantendo interface unica para `NoteService`.

## Funcionalidades principais

- Cadastro e login com as mesmas regras do projeto original (validacao de login e senha forte em [app/models/usuario.py](app/models/usuario.py)).
- Criacao, edicao e exclusao de notas usando comandos.
- Visualizacao de historico (timestamps) e desfazer com Memento diretamente na interface.
- Anexo de arquivos armazenados na pasta `uploads/` com rastreabilidade no repositório.
- Troca de estrategia de persistencia (RAM ou JSON) com um clique, sem reiniciar a aplicacao.

## Estrategia de log

- `ConsoleLogTarget` envia logs para o terminal.
- `FileLogTarget` grava o mesmo texto em `logs/app.log`.
- `LoggerAdapter` entrega metodos `info` e `error` consumidos pelos serviços.

## Testes manuais sugeridos

1. Registrar um usuario novo, fazer login e criar notas com anexos.
2. Alternar entre estrategia JSON e memoria para perceber as mudancas persistentes.
3. Editar uma nota varias vezes e usar **Desfazer** para restaurar cada estado.
4. Reabrir o app e conferir a leitura do arquivo `data/notes.json` e do historico exibido.

## Proximos passos possiveis

- Adicionar exportacao de nota em PDF usando Template Method.
- Expandir o Adapter de logs para integracoes remotas (HTTP, syslog etc).
- Criar testes automatizados para os comandos e para o caretaker.

