# 🐳 Guia de Uso com Docker

Este guia explica como rodar o projeto Finance Agent usando Docker e Docker Compose.

## 📋 Pré-requisitos

- **Docker**: [Instale aqui](https://docs.docker.com/get-docker/)
- **Docker Compose**: [Instale aqui](https://docs.docker.com/compose/install/)
- **Groq API Key**: Obtenha em https://console.groq.com

## 🚀 Quick Start

### 1. Configurar Variáveis de Ambiente

```bash
# Copie o arquivo de exemplo
cp .env.docker .env

# Edite o .env e adicione suas credenciais
# Você PRECISA adicionar sua chave Groq
export GROQ_API_KEY=gsk_xxxxxxxxxxxxx
```

### 2. Criar a Collection no Qdrant (Primeira vez)

```bash
# Execute com o profile "init" para rodar o script de criar a collection
docker-compose --profile init up create-collection

# Espere a mensagem de sucesso, depois pressione Ctrl+C
```

**O que acontece:**
- ✅ Qdrant inicia e fica saudável
- ✅ Script `create_collection` conecta ao Qdrant
- ✅ Deleta a collection "financial" (se existir)
- ✅ Cria uma nova collection com configuração otimizada

### 3. Iniciar a API

```bash
# Inicie todos os serviços
docker-compose up

# Ou em background:
docker-compose up -d
```

**Serviços que iniciam:**
- **Qdrant** em `http://localhost:6333`
- **API** em `http://localhost:8000`
- **Swagger Docs** em `http://localhost:8000/docs`

### 4. Usar a API

```bash
# Testar análise de um ticker
curl -X POST "http://localhost:8000/agent" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Apple é um bom investimento?",
    "limit": 3
  }'

# Buscar informações
curl -X POST "http://localhost:8000/search" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Receita da Apple em 2023",
    "limit": 5
  }'
```

## 🔧 Comandos Úteis

### Iniciar Serviços
```bash
# Iniciar todos os serviços
docker-compose up

# Iniciar em background
docker-compose up -d

# Iniciar apenas qdrant (útil para testes)
docker-compose up qdrant
```

### Ver Logs
```bash
# Ver logs de todos os serviços
docker-compose logs -f

# Ver logs de um serviço específico
docker-compose logs -f api
docker-compose logs -f qdrant
docker-compose logs -f create-collection
```

### Parar Serviços
```bash
# Parar todos os serviços
docker-compose down

# Parar mantendo volumes (dados persistem)
docker-compose down

# Parar e remover volumes (limpa tudo)
docker-compose down -v
```

### Reconstruir Imagens
```bash
# Reconstruir a imagem do projeto
docker-compose build

# Forçar rebuild sem cache
docker-compose build --no-cache
```

### Executar Comandos Dentro do Container
```bash
# Executar comando no container api
docker-compose exec api python -c "print('Hello')"

# Abrir shell interativo
docker-compose exec api bash
```

## 🔄 Re-criar a Collection

Se você quiser resetar a collection (deletar e recriar):

```bash
# Option 1: Usando o profile init
docker-compose --profile init up create-collection

# Option 2: Manualmente no container
docker-compose exec api python -m api.ingestion.create_collection
```

## 🌐 Qdrant Dashboard

Acesse o Qdrant Web UI em: **http://localhost:6333/dashboard**

Aqui você pode:
- Ver collections
- Visualizar pontos (vetores)
- Testar buscas
- Monitorar performance

## 🔐 Segurança em Produção

### Mudar Chave de API do Qdrant

```bash
# Em .env
QDRANT_API_KEY=sua-chave-secreta-aqui
```

### Não Expor Portas Desnecessárias

Para produção, modifique o docker-compose.yml:

```yaml
services:
  qdrant:
    # Remova ou comente a seção "ports" para não expor
    # ports:
    #   - "6333:6333"
    #   - "6334:6334"
```

### Usar .env.local (não incluir no git)

```bash
# .gitignore
.env
.env.local
```

## 📊 Estrutura de Volumes

- **qdrant_storage**: Persiste dados do Qdrant entre restarts
- **-v .:/app**: Monta o código local (hot reload com --reload)

## 🐛 Troubleshooting

### Qdrant não inicia

```bash
# Verificar logs
docker-compose logs qdrant

# Resetar volumes
docker-compose down -v
docker-compose up
```

### API não consegue conectar ao Qdrant

```bash
# Verificar se Qdrant está saudável
docker-compose ps

# Ver logs da API
docker-compose logs api
```

### Create Collection falha

```bash
# Verificar logs
docker-compose --profile init logs create-collection

# Verificar se .env tem GROQ_API_KEY
cat .env | grep GROQ_API_KEY

# Tentar manualmente
docker-compose --profile init run --rm create-collection
```

### Porta 8000 ou 6333 já em uso

```bash
# Trocar porta no docker-compose.yml
# Altere "8000:8000" para "8001:8000" por exemplo

# Ou liberar a porta
# macOS/Linux:
lsof -i :8000
kill -9 <PID>
```

## 📈 Performance Tips

### Usar BuildKit (mais rápido)

```bash
DOCKER_BUILDKIT=1 docker-compose build
```

### Limpar Cache do Docker

```bash
# Remover imagens não usadas
docker image prune

# Remover containers parados
docker container prune

# Limpeza completa (cuidado!)
docker system prune -a
```

## 🚀 Deploy

Para deploy em produção, veja as melhores práticas:

1. Use `.env` com variáveis de produção
2. Configure QDRANT_URL para instância cloud
3. Use health checks
4. Configure resource limits
5. Use reverse proxy (nginx)
6. Configure logging centralizado

## 📝 Exemplo Completo de .env para Docker

```env
# Qdrant Configuration
QDRANT_API_KEY=sua-chave-super-secreta

# Groq API (necessário)
GROQ_API_KEY=gsk_xxxxxxxxxxxxxxxxxxxxxx

# OpenAI API (opcional)
OPENAI_API_KEY=sk_xxxxxxxxxxxxx

# Para usar Qdrant Cloud em vez de local:
# QDRANT_URL=https://xxxxx-xxxxx.us-east-1-0.aws.cloud.qdrant.io
# QDRANT_API_KEY=xxxxxxxxxxxxxxxx
```

## ✅ Checklist de Setup

- [ ] Docker e Docker Compose instalados
- [ ] Groq API Key obtida
- [ ] .env arquivo criado com credenciais
- [ ] `docker-compose --profile init up create-collection` executado
- [ ] API acessível em http://localhost:8000
- [ ] Swagger docs visível em http://localhost:8000/docs
- [ ] Primeiro teste de endpoint bem-sucedido

---

Para mais informações, veja [README.md](README.md)
