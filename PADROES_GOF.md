# Padrões de Projeto GOF — RigTech

Documento descritivo com indicação das classes envolvidas e do objetivo de uso de cada padrão no projeto.

---

## Padrões Criacionais

---

### 1. Abstract Factory

**Classes envolvidas:**
- `StorageStrategy` (protocol/interface)
- `JsonStorageStrategy`
- `InMemoryStorageStrategy`
- `InterfaceStrategy` (ABC)
- `GuiInterfaceStrategy`
- `RestApiInterfaceStrategy`

**Objetivo no projeto:**
Provê famílias de objetos relacionados sem acoplamento a implementações concretas. No projeto, `StorageStrategy` define a interface para criar estratégias de persistência (JSON ou memória), enquanto `InterfaceStrategy` faz o mesmo para interfaces de usuário (GUI ou API REST). Cada família pode ser trocada de forma transparente apenas alterando a implementação instanciada.

---

### 2. Factory Method

**Classes envolvidas:**
- `CommandFactory`
- `CreateNoteCommand`
- `UpdateNoteCommand`
- `DeleteNoteCommand`
- `AttachFileCommand`
- `AttachContentCommand`

**Objetivo no projeto:**
Centraliza a criação de todos os objetos de comando do sistema. `CommandFactory` expõe métodos de fábrica (`create_note`, `update_note`, `delete_note`, `attach_file`, `attach_content`) que instanciam o comando concreto correto sem que o chamador precise conhecer as classes internas. Isso desacopla a interface (GUI/API) dos detalhes de construção dos comandos.

---

### 3. Prototype

**Classes envolvidas:**
- `Note` (método `clone`)

**Objetivo no projeto:**
Permite criar cópias independentes de uma nota sem depender de sua classe concreta. O método `Note.clone()` serializa a nota para dicionário e a reconstrói via `from_dict`, garantindo uma cópia profunda. É utilizado internamente pelo padrão Memento para preservar o estado da nota antes de operações de edição ou exclusão.


---

## Padrões Estruturais

---

### 4. Adapter

**Classes envolvidas:**
- `LoggerAdapter`
- `LegacyLogTarget` (Protocol)
- `ConsoleLogTarget`
- `FileLogTarget`

**Objetivo no projeto:**
Adapta diferentes destinos de log (`ConsoleLogTarget` e `FileLogTarget`) a uma interface uniforme esperada pelo restante do sistema. `LoggerAdapter` recebe qualquer objeto compatível com `LegacyLogTarget` e expõe métodos padronizados (`info`, `error`), permitindo trocar o destino do log sem alterar os serviços que o utilizam.

---

### 5. Bridge

**Classes envolvidas:**
- `NoteRepository`
- `UserRepository`
- `TalhaoRepository`
- `StorageStrategy` (protocol)
- `JsonStorageStrategy`
- `InMemoryStorageStrategy`

**Objetivo no projeto:**
Separa a abstração (repositórios) da implementação (estratégias de armazenamento), permitindo que ambas evoluam independentemente. Os repositórios delegam operações de persistência à estratégia injetada, tornando possível alternar entre armazenamento em arquivo JSON e armazenamento em memória sem modificar a lógica dos repositórios.

---

## Padrões Comportamentais

---

### 6. Chain of Responsibility

**Classes envolvidas:**
- `AttachmentValidator` (elo base abstrato)
- `ContentValidator`
- `SizeValidator`
- `FormatValidator`
- `build_attachment_chain` (função montadora)

**Objetivo no projeto:**
Valida arquivos anexados a notas por meio de uma cadeia de validadores encadeados. Cada elo verifica um aspecto do arquivo (conteúdo não vazio → tamanho dentro do limite → extensão permitida) e repassa ao próximo. Se qualquer elo rejeitar o arquivo, a operação é interrompida com uma exceção. A cadeia padrão é: `ContentValidator → SizeValidator → FormatValidator`.

---

### 7. Command

**Classes envolvidas:**
- `BaseNoteCommand` (ABC)
- `CreateNoteCommand`
- `UpdateNoteCommand`
- `DeleteNoteCommand`
- `AttachFileCommand`
- `AttachContentCommand`
- `CommandInvoker`
- `CommandSender`

**Objetivo no projeto:**
Encapsula cada operação sobre notas como um objeto independente, possibilitando execução, histórico e desfazer (undo). `CommandSender` despacha comandos ao `CommandInvoker`, que salva o snapshot via Memento antes da execução e mantém histórico para reverter operações. Esse padrão desacopla completamente a interface de usuário da lógica de negócio.

---

### 8. Mediator

**Classes envolvidas:**
- `NoteEventBus`
- `SatelliteEventBus`
- `NoteObserver` (ABC)
- `SatelliteObserver` (ABC)
- `LogNoteObserver`
- `StatisticsObserver`
- `LogSatelliteObserver`

**Objetivo no projeto:**
Centraliza a comunicação entre componentes do sistema, evitando dependências diretas entre eles. `NoteEventBus` e `SatelliteEventBus` atuam como mediadores: os serviços emitem eventos sem conhecer quem os escuta, e os observadores reagem sem conhecer a origem. Isso mantém os módulos desacoplados e facilita a adição de novos comportamentos reativos.

---

### 9. Memento

**Classes envolvidas:**
- `NoteMemento`
- `NoteCaretaker`
- `NoteReceiver` (usa snapshot/restore)

**Objetivo no projeto:**
Preserva o estado de uma nota antes de operações destrutivas (edição, exclusão, anexo), permitindo desfazê-las. `NoteMemento` armazena o estado serializado da nota com timestamp. `NoteCaretaker` mantém uma pilha de mementos por nota e por ordem global. O `CommandInvoker` consulta o caretaker ao executar `undo_last`.

---

### 10. Observer

**Classes envolvidas:**
- `NoteObserver` (ABC)
- `LogNoteObserver`
- `StatisticsObserver`
- `NoteEventBus`
- `SatelliteObserver` (ABC)
- `LogSatelliteObserver`
- `SatelliteEventBus`
- `EventoNota` (Enum)
- `EventoSatelite` (Enum)

**Objetivo no projeto:**
Notifica automaticamente múltiplos componentes quando eventos ocorrem no sistema, sem acoplamento direto. Quando uma nota é criada, atualizada ou removida, `NoteEventBus.emitir` dispara `notificar` em todos os observadores registrados: `LogNoteObserver` registra o evento no log e `StatisticsObserver` contabiliza métricas de uso. O mesmo mecanismo se aplica a eventos de satélite.

---

### 11. Strategy

**Classes envolvidas:**
- `StorageStrategy` (Protocol)
- `JsonStorageStrategy`
- `InMemoryStorageStrategy`
- `InterfaceStrategy` (ABC)
- `GuiInterfaceStrategy`
- `RestApiInterfaceStrategy`

**Objetivo no projeto:**
Permite trocar algoritmos e comportamentos em tempo de configuração sem alterar o código cliente. `StorageStrategy` define como os dados são persistidos (arquivo JSON ou memória volátil), configurável pela constante `ACTIVE_STORAGE` em `main.py`. `InterfaceStrategy` define qual interface o sistema expõe (GUI desktop ou API REST), configurável por `ACTIVE_INTERFACE`.

---

### 12. Template Method

**Classes envolvidas:**
- `NoteExporter` (ABC — define o esqueleto)
- `PdfNoteExporter`
- `PlainTextNoteExporter`

**Objetivo no projeto:**
Define o esqueleto do algoritmo de exportação de notas em etapas fixas (`_setup → _write_header → _write_body → _write_footer → _build`), delegando cada etapa às subclasses. `PdfNoteExporter` gera um arquivo PDF formatado usando a biblioteca `fpdf2`, enquanto `PlainTextNoteExporter` gera texto simples. O método `export` em `NoteExporter` não pode ser sobrescrito, garantindo a ordem das etapas.

---

## Resumo

| # | Padrão               | Categoria    | Implementado | Arquivo principal               |
|---|----------------------|--------------|--------------|---------------------------------|
| 1 | Abstract Factory     | Criacional   | Sim          | `repository/strategies.py`, `interface/interface_strategy.py` |
| 2 | Builder              | Criacional   | Não          | —                               |
| 3 | Factory Method       | Criacional   | Sim          | `patterns/factory.py`           |
| 4 | Prototype            | Criacional   | Sim          | `models/note.py`                |
| 5 | Singleton            | Criacional   | Não          | —                               |
| 6 | Adapter              | Estrutural   | Sim          | `utils/logger_adapter.py`       |
| 7 | Bridge               | Estrutural   | Sim          | `repository/`, `repository/strategies.py` |
| 8 | Composite            | Estrutural   | Não          | —                               |
| 9 | Decorator            | Estrutural   | Não          | —                               |
|10 | Facade               | Estrutural   | Não          | —                               |
|11 | Flyweight            | Estrutural   | Não          | —                               |
|12 | Proxy                | Estrutural   | Não          | —                               |
|13 | Chain of Responsibility | Comportamental | Sim       | `patterns/chain.py`             |
|14 | Command              | Comportamental | Sim          | `patterns/command.py`, `patterns/sender.py` |
|15 | Interpreter          | Comportamental | Não          | —                               |
|16 | Iterator             | Comportamental | Não          | —                               |
|17 | Mediator             | Comportamental | Sim          | `patterns/observer.py`          |
|18 | Memento              | Comportamental | Sim          | `patterns/memento.py`           |
|19 | Observer             | Comportamental | Sim          | `patterns/observer.py`          |
|20 | State                | Comportamental | Não          | —                               |
|21 | Strategy             | Comportamental | Sim          | `repository/strategies.py`, `interface/interface_strategy.py` |
|22 | Template Method      | Comportamental | Sim          | `patterns/export.py`            |
|23 | Visitor              | Comportamental | Não          | —                               |
