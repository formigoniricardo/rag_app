# 🔮 Oráculo Corporativo — RAG AI

Sistema de Recuperação Aumentada por Geração (RAG) que transforma documentos estáticos em uma base de conhecimento consultável via chat. Utiliza Google Gemini como LLM, PostgreSQL + pgvector para armazenamento vetorial e Streamlit como interface. Roda inteiramente em containers Docker com Alpine no GitHub Codespaces.

---

## 🌐 Aplicação em Produção

O Oráculo Corporativo já está no ar! Você pode acessar e testar o sistema em tempo real clicando no botão abaixo:

[![Acessar Aplicação](https://img.shields.io/badge/_Acessar_Aplicação-46E3B7?style=for-the-badge&logo=render&logoColor=black)](https://rag-app-zg4k.onrender.com)

---

## Tecnologias

- **Python 3.12** · **Streamlit** · **Google Gemini** (embeddings + LLM)
- **PostgreSQL 16 + pgvector** · **Docker + Alpine** · **LangChain**
- **pypdf** (leitura de PDF) · **fpdf2** (geração de PDF) · **psycopg2** (PostgreSQL)

## Arquitetura

```
Usuário ──► Streamlit (porta 8501)
                │
                ├─ Upload (PDF/TXT/CSV) → chunking → embeddings → PostgreSQL
                │
                ├─ Pergunta → Gemini Embeddings → vetor
                │                                    │
                ├─ Busca por similaridade ◄──── PostgreSQL + pgvector
                │
                └─ Contexto + Pergunta → Gemini LLM → Resposta + Fontes
                                                         │
                                                         └─ Download em PDF
```

---

## Pré-requisito

Uma chave da API Google Gemini — obtenha grátis em [aistudio.google.com](https://aistudio.google.com/)

---

## Como rodar no GitHub Codespaces

### 1. Configurar a chave da API (uma vez só)

Primeiro Fork o Projeto e depois vá nas configurações do seu github (não do projeto), ou seja, em **github.com** → clique no seu **avatar** (canto superior direito) → **Settings** → no menu lateral, seção **"Code, planning, and automation"**, clique em **Codespaces** → **Secrets** → **New secret**:

| Campo | Valor |
|-------|-------|
| **Name** | `CHAVE_API_GOOGLE` |
| **Value** | sua chave do Gemini |
| **Repository access** | selecione o repositório `rag_app` |

Ou renomeie adicione um .env no githubspaces para ter acesso a chave com a Key do gemini, com CHAVE_API_GOOGLE=sua_chave_aqui, se não quiser forkar a repo.

### 2. Abrir o Codespace

No repositório, clique em **Code** → **Codespaces** → **Create codespace on main**.

Aguarde o ambiente carregar (o devcontainer instala Docker automaticamente).

### 3. Subir a aplicação

No terminal do Codespace, execute:

```bash
docker compose up --build
```

O primeiro build leva alguns minutos (Alpine compilando dependências). Builds seguintes são instantâneos graças ao cache do Docker.

Aguarde até ver no log:

```
You can now view your Streamlit app in your browser.
```

### 4. Acessar a aplicação

Na aba **Ports** (parte inferior do VS Code), clique no 🌐 da porta **8501**.

Se aparecer erro 401 (Unauthorized), clique com o botão direito na porta 8501 → **Port Visibility** → **Public**. Depois clique no link novamente.

### 5. Carregar dados no banco

**Opção A — Pela interface (recomendado):**

No sidebar da aplicação, use **Upload de documentos** → baixei do repositório, os arquivos que constam na pasta data_example envie um desses arquivos `.pdf`, `.txt` ou `.csv`, clicando em **Indexar arquivo** (só pode enviar um por vez).

**Opção B — Pelo terminal (dados de exemplo):**

Abra um segundo terminal no Codespace e execute:

```bash
docker compose exec app python -m consume_api.insert_data_in_database.inserir_dados_postgres
```

### 6. Usar

Digite uma pergunta no chat e veja a resposta com as fontes do banco. Use o botão **📥 Baixar conversa em PDF** no sidebar para exportar o histórico.

---

## Como rodar localmente (Docker Desktop)

### 1. Pré-requisitos locais

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) instalado e rodando
- [Git](https://git-scm.com/) instalado

### 2. Clonar o repositório

```bash
git clone https://github.com/GabrielMS92/rag_app.git
cd rag_app
```

### 3. Configurar a chave da API

```bash
cp .env.example .env
```

Abra o arquivo `.env` no VS Code e substitua `cole_sua_chave_aqui` pela sua chave do Gemini:

```
CHAVE_API_GOOGLE=sua_chave_aqui
```

> **Importante:** o `.env` está no `.gitignore` e nunca será enviado ao GitHub.
> **Nota:** se o `.env` e o Codespace Secret existirem ao mesmo tempo, o Secret tem precedência. Não há conflito.

### 4. Subir a aplicação

No terminal do VS Code (`` Ctrl+` `` para abrir), execute:

```bash
docker compose up --build
```

Aguarde até ver `You can now view your Streamlit app in your browser.`

### 5. Acessar

Abra no navegador: **http://localhost:8501**

### 6. Carregar dados e usar

Mesmo processo do Codespaces: upload pelo sidebar ou pelo terminal:

```bash
docker compose exec app python -m consume_api.insert_data_in_database.inserir_dados_postgres
```

---

## Comandos úteis

| Ação | Comando |
|------|---------|
| **Subir a aplicação** | `docker compose up --build` |
| **Subir em background** | `docker compose up --build -d` |
| **Parar a aplicação** | `docker compose down` |
| **Parar e apagar os dados do banco** | `docker compose down -v` |
| **Rebuild (após alterar código)** | `docker compose up --build` |
| **Ver logs** | `docker compose logs -f app` |
| **Carregar dados de exemplo** | `docker compose exec app python -m consume_api.insert_data_in_database.inserir_dados_postgres` |
| **Abrir shell no container** | `docker compose exec app sh` |

---

## Requisitos Funcionais

| RF | Descrição | Status |
|----|-----------|--------|
| RF01 | Upload de arquivos (PDF, TXT, CSV) pela interface | ✅ |
| RF02 | Fragmentação em chunks | ✅ |
| RF03 | Geração de embeddings via Gemini | ✅ |
| RF04 | Armazenamento vetorial no PostgreSQL | ✅ |
| RF05 | Conversão da pergunta em vetor | ✅ |
| RF06 | Recuperação por similaridade | ✅ |
| RF07 | Resposta fundamentada no contexto | ✅ |
| RF08 | Histórico de mensagens na sessão | ✅ |
| RF09 | Limpeza / reinício da base | ✅ |
| RF10 | Status de processamento na interface | ✅ |
| RF11 | Ajuste de temperatura da IA | ✅ |
| RF12 | Citação de fontes dos documentos | ✅ |

## Requisitos Não-Funcionais

| RNF | Descrição | Como foi atendido |
|-----|-----------|-------------------|
| RNF01 | Resposta em até 10s | Busca vetorial + Gemini Flash atingem ~3-5s |
| RNF02 | Suportar milhares de fragmentos | PostgreSQL + pgvector com busca exata |
| RNF03 | Credenciais via variáveis de ambiente | Codespace Secrets, sem chaves no código |
| RNF04 | Interface intuitiva | Streamlit com chat, sidebar e feedback visual |
| RNF05 | Portabilidade via Docker | Dockerfile Alpine + docker-compose |

---

## Melhorias da C3 em relação à C2

1. **Bug crítico corrigido**: a ingestão gravava na tabela `documentos` via SQL, mas a busca usava o PGVector do LangChain (tabelas internas `langchain_pg_*`). Os dados nunca eram encontrados. Agora ambos usam a mesma tabela com SQL direto.
2. **Modelo de embedding unificado**: ingestão usava `gemini-embedding-001`, busca usava `gemini-embedding-2` (vetores incompatíveis). Agora ambos usam `gemini-embedding-001`.
3. **Credenciais removidas do código**: host e senha hardcoded substituídos por variáveis de ambiente.
4. **RF01 completo**: upload agora aceita PDF, TXT e CSV (antes só TXT).
5. **Interface evoluída**: chat com histórico, slider de temperatura, reset da base, fontes, e download em PDF.
6. **Containerização completa**: Dockerfile Alpine + docker-compose + devcontainer para Codespaces.
7. **Embeddings em lote**: ingestão otimizada com `embed_documents` (batch) em vez de uma chamada por chunk.
8. **Schema auto-criado**: `init.sql` + `garantir_schema()` eliminam setup manual do banco.
9. **Download de respostas**: exportação do histórico de conversa em PDF.

---

## Variáveis de ambiente

| Variável | Padrão | Descrição |
|----------|--------|-----------|
| `CHAVE_API_GOOGLE` | — | Chave Gemini (obrigatória) |
| `DB_HOST` | `localhost` | Host do banco |
| `DB_PORT` | `5432` | Porta |
| `DB_NAME` | `rag_db` | Nome do banco |
| `DB_USER` | `postgres` | Usuário |
| `DB_PASSWORD` | `senha123` | Senha |
| `LLM_TEMPERATURE` | `0.4` | Temperatura do modelo |
| `RAG_TOP_K` | `5` | Chunks recuperados por busca |

---

## Estrutura do projeto

```
rag_app/
├── consume_api/
│   ├── interface_main.py             # Interface Streamlit (chat + sidebar + download PDF)
│   ├── rag_core.py                   # Cadeia RAG, busca vetorial, ingestão, geração de PDF
│   └── insert_data_in_database/
│       ├── inserir_dados_postgres.py  # Ingestão via terminal
│       └── make_chunks.py            # Chunking com LangChain
├── data_example/
│   └── wiki_nexus_monitor.txt        # Dados fictícios da TechVision Solutions
├── docs/                             # Documentação C1, C2 e quadro de avaliações
├── .devcontainer/devcontainer.json   # Configuração do GitHub Codespaces
├── Dockerfile                        # Imagem Alpine da aplicação
├── docker-compose.yml                # Orquestração App + PostgreSQL/pgvector
├── init.sql                          # Schema inicial do banco (extensão + tabela)
├── requirements.txt                  # Todas as dependências Python pinadas
└── .env.example                      # Modelo de variáveis de ambiente
```

---

## Lições aprendidas

- Ingestão e busca devem usar o **mesmo modelo de embeddings** — vetores de modelos diferentes não são comparáveis, causando resultados vazios mesmo com dados no banco.
- O PGVector do LangChain cria tabelas próprias (`langchain_pg_collection` / `langchain_pg_embedding`). Quando a ingestão é feita por SQL direto, a busca também precisa ser por SQL direto na mesma tabela.
- Variáveis de ambiente e Codespace Secrets são essenciais para portabilidade e segurança — permitem mover de local para Docker para nuvem sem alterar código e sem expor credenciais.
- Alpine reduz o tamanho da imagem Docker, mas exige atenção a dependências que precisam de compilação C/Rust (`gcc`, `musl-dev`, `postgresql-dev`, `cargo`).
- O `docker-in-docker` no Codespaces precisa de `"moby": false` porque a imagem base Python agora usa Debian Trixie, que não tem o pacote `moby-cli`.

---

## Troubleshooting

| Problema | Solução |
|----------|---------|
| Erro 401 ao abrir a URL | Na aba Ports, clique direito na 8501 → Port Visibility → Public |
| Build muito lento no Alpine | Troque `alpine` por `slim-bookworm` na linha 3 do Dockerfile |
| `connection refused` ao banco | Aguarde o healthcheck: `docker compose ps` → db deve estar `healthy` |
| Porta 8501 não aparece | Aba Ports → Adicionar Porta → `8501` |
| Codespace não sobe (recovery mode) | Verifique se o devcontainer.json tem `"moby": false` |
| Chave da API não funciona | Confirme que o secret está em Settings do **perfil** → Codespaces → Secrets (não em Actions) |

---

## Preview

[![Preview](https://img.youtube.com/vi/KkOIZ0o1Y98/maxresdefault.jpg)](https://youtu.be/KkOIZ0o1Y98)

[![Assistir no YouTube](https://img.shields.io/badge/▶_Assistir_Preview-red?style=for-the-badge&logo=youtube)](https://youtu.be/KkOIZ0o1Y98)

---

## Próximos passos

- Autenticação de usuários com controle de sessão e permissões.
- Índice vetorial HNSW ou IVFFlat para bases com milhões de chunks.
- Deploy permanente em nuvem (Como Azure App Service + Azure Database for PostgreSQL ou outros Serviços).
- Suporte a mais formatos de entrada (DOCX, JSON, HTML).
- Persistência do histórico de chat no banco de dados.
- Painel administrativo com métricas de uso e qualidade das respostas.

---

## Autores

- [Addriel Teixeira Pereira](https://github.com/addrielteixeira)
- [Gabriel Moreira da Silva](https://github.com/GabrielMS92)
- [Renato Oliveira de Jesus](https://github.com/RenatoOJ-Dev)
- [Ricardo Formigoni Souza](https://github.com/formigoniricardo)

**Disciplina:** Desenvolvimento de Aplicações Web II — 2026/1
**Professor:** Otávio Lube dos Santos
**Instituição:** FAESA — Centro Universitário Espírito-santense
