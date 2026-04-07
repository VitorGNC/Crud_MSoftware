# RigTech — Status do Projeto

**Data:** 06/04/2026  
**Equipe:** Ícaro Oliveira, Vitor Gabriel, Guilherme Peixoto, João Pedro Chaves, João Marcos Santos  
**Disciplina:** Manutenção de Software — UFPB

---

## 1. O que foi implementado

### Interface Gráfica (GUI)
- [x] Janela principal com branding **RigTech** (título, logo na sidebar)
- [x] Tela inicial com nome "RigTech" centralizado e subtítulo "Plataforma de Analise Agricola"
- [x] **Barra lateral** com 7 botões de navegação:
  - Anotacoes
  - Upload Imagem Drone
  - Mostrar Shapefile *(placeholder)*
  - Mostrar Talhoes *(placeholder)*
  - Criar Talhao *(placeholder)*
  - Processar *(placeholder)*
  - Mostrar Dados *(placeholder)*
- [x] Telas placeholder para funcionalidades futuras com indicação "Em desenvolvimento"

### Autenticação e Usuários
- [x] Tela de login e registro de usuário
- [x] Validação de credenciais
- [x] Persistência de usuários em `data/usuarios.json`

### Módulo de Anotações (CRUD completo)
- [x] Criar, editar, excluir e listar notas
- [x] Anexar arquivos a notas
- [x] Histórico de edições (Memento)
- [x] Operação de desfazer (Undo)
- [x] Persistência em `data/notes.json`
- [x] Exportação de notas em **PDF** (Template Method com fpdf2)
- [x] Exportação de notas em texto puro

### Upload de Imagem de Drone (RF06 — parcial)
- [x] Tela dedicada com instruções e formatos suportados (GeoTIFF)
- [x] Seleção de arquivo via explorador de arquivos
- [x] Cópia do arquivo para `data/drone_images/`
- [x] Registro do upload em `data/drone_uploads.json` com: nome, caminho original, caminho salvo, usuário e data/hora
- [x] Tratamento de arquivos duplicados (sufixo de timestamp)

### API REST (alternativa à GUI)
- [x] API FastAPI disponível via `ACTIVE_INTERFACE = "api"` em `main.py`
- [x] Endpoints para CRUD de notas

### Design Patterns implementados
| Pattern | Onde |
|---|---|
| Command + Invoker | `app/patterns/command.py`, `sender.py`, `receiver.py` |
| Memento | `app/patterns/memento.py` |
| Observer | `app/patterns/observer.py` |
| Chain of Responsibility | `app/patterns/chain.py` |
| Strategy | `app/repository/strategies.py`, `app/interface/interface_strategy.py` |
| Factory | `app/patterns/factory.py` |
| Adapter | `app/utils/logger_adapter.py` |
| Template Method | `app/patterns/export.py` |

### Persistência
- [x] Estratégia JSON (`data/notes.json`, `data/usuarios.json`, `data/drone_uploads.json`)
- [x] Estratégia em memória (para testes)
- [x] Pasta `data/drone_images/` para armazenamento de imagens

---

## 2. O que está faltando (por requisito)

### RF01 — Processamento de Imagens e Detecção de Anomalias
- [ ] Integração com API do satélite **Sentinel-2**
- [ ] Cálculo de índices de vegetação **NDVI / EVI**
- [ ] Análise geoespacial para identificação de áreas problemáticas
- [ ] Sistema de alertas ao produtor com localização da anomalia
- [ ] Meta: taxa de assertividade mínima de 70%

### RF02 — Visualização de Propriedade e Camadas Vetoriais
- [ ] Carregamento e renderização de arquivos **Shapefile** (.shp / .zip)
- [ ] Interface de mapa (satélite / ortomosaico) como base
- [ ] Sobreposição (overlay) de camadas vetoriais sobre o mapa
- [ ] Suporte ao sistema de coordenadas SIRGAS 2000 / WGS84
- [ ] Zoom e pan com camadas carregadas

### RF03 — Navegação Ágil e Visualização de Talhões
- [ ] Listagem e seleção de talhões da propriedade
- [ ] Zoom automático ("Zoom to Layer") ao selecionar talhão
- [ ] Carregamento de camadas geográficas em menos de 20 segundos
- [ ] Acesso ao talhão em no máximo 4 cliques

### RF04 — Geração de Cartografia e Dashboards
- [ ] Mapas temáticos georreferenciados
- [ ] Relatórios com indicadores: tamanho do talhão, impacto financeiro, área de daninhas
- [ ] Exportação dos mapas/relatórios em **PDF agronômico**
  *(a exportação PDF de notas existe, mas não de relatórios agrícolas)*

### RF05 — Detecção de Daninhas e Formigueiros
- [ ] Processamento de imagens de alta resolução por visão computacional
- [ ] Identificação de **Mamona** (planta daninha latifoliada)
- [ ] Identificação de **formigueiros** (montículos de terra)
- [ ] Geração de coordenadas geográficas ou polígonos de infestação
- [ ] Compatibilidade com mapas georreferenciados

### RF06 — Upload de Imagens de Drone *(parcialmente implementado)*
- [x] Seleção e cópia de arquivo GeoTIFF local
- [x] Registro de metadados em JSON
- [ ] Suporte robusto a arquivos de até **25 GB** (upload chunked / streaming)
- [ ] Vinculação automática à fazenda/talhão por coordenadas geográficas da imagem

### RNF001 — Usabilidade
- [ ] Interface **web responsiva** (atual é desktop Tkinter)
- [ ] Geração de relatório completo em no máximo 5 cliques

### RNF002 — Desempenho
- [ ] Processamento de ortomosaico em ≤ 10 minutos por 100 ha
- [ ] Integração com GPU (Google Colab A100 ou equivalente)

### RNF003 — Disponibilidade de Dados
- [ ] Atualização automática de dados de satélite a cada **5 dias**
- [ ] Chamadas automáticas via API para novos índices NDVI/EVI

### RNF004 — Segurança
- [ ] Autenticação via **OAuth2 ou JWT** (atual é login simples)
- [ ] Criptografia em repouso **AES-256**
- [ ] Comunicação via **TLS 1.2+**

---

## 3. Próximos Passos (sugestão de prioridade)

### Alta Prioridade
1. **Tela de Talhões (RF03):** implementar listagem, criação e seleção de talhões com persistência JSON
2. **Tela Criar Talhão (RF03):** formulário com nome, área (ha) e coordenadas básicas
3. **Vinculação imagem → talhão (RF06):** ao fazer upload, associar a imagem ao talhão correspondente
4. **Segurança básica (RNF004):** migrar autenticação para JWT com hash de senha (bcrypt)

### Média Prioridade
5. **Visualização Shapefile (RF02):** integrar biblioteca `geopandas` + `matplotlib` para renderizar .shp na tela
6. **Relatório agrícola em PDF (RF04):** adaptar o `PdfNoteExporter` existente para relatórios de talhão com indicadores
7. **Tela Mostrar Dados (RF04):** dashboard com estatísticas dos talhões e uploads

### Baixa Prioridade / Longo Prazo
8. **Detecção de daninhas/formigueiros (RF05):** modelo de visão computacional (YOLOv8 ou similar)
9. **Integração Sentinel-2 (RF01):** consumo de API para NDVI/EVI com alertas automáticos
10. **Upload chunked de 25 GB (RF06):** substituir `shutil.copy2` por upload em partes com barra de progresso
11. **Migração para interface web (RNF001):** substituir Tkinter por aplicação web (FastAPI + frontend)
12. **Atualização automática de satélite (RNF003):** agendador de tarefas (APScheduler ou cron)
