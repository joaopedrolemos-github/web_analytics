# Pulso Commerce — contexto para o Claude Code

## Objetivo
Projeto de portfólio para migração de carreira para **Analytics Engineer**. Mostra engenharia de dados ponta a ponta no Databricks e o mesmo modelo semântico consumido por três ferramentas, além do uso de IA (chatbot de perguntas de negócio e dashboard HTML).

## Regras (obrigatórias)
1. **Databricks**: Bronze + Silver + Gold + Camada Semântica + Unity Catalog + Dashboard + Chatbot (Genie)
2. **Power BI**: Dashboard + RLS
3. **Claude**: Chatbot + Dashboard (página HTML feita com Claude; Lovable foi descartado)

## Ambiente
- Databricks **Free Edition** (só compute serverless; recursos de admin limitados)
- Repositório público no GitHub: `web_analytics`; README em PT (`README.md`) e EN (`README.en.md`)
- Projeto feito em partes pequenas, validando cada uma antes da próxima

## Dados
- Base: Olist Brazilian E-commerce (Kaggle, ~100 mil pedidos, 2016–2018, 9 tabelas), baixado via API do Kaggle
- Chegada simulada: histórico do Olist reproduzido em lotes por data no Volume `landing.raw` (Auto Loader incremental)
- Sintéticos (Python, em `data-generator/`): clickstream web (~10–15 sessões sem conversão por pedido) + investimento diário em mídia, ligados aos pedidos reais; atribuição last-click

## Arquitetura
- Unity Catalog: catálogos `pulso_dev` e `pulso_prd`; schemas `landing`, `bronze`, `silver`, `gold`, `semantic`, `ops`
- Pipeline: Lakeflow Declarative Pipelines (Auto Loader → expectations no Silver → star schema no Gold)
- Gold:
  - Dimensões: `dim_cliente`, `dim_seller` (SCD2), `dim_produto`, `dim_data`, `dim_geografia`, `dim_canal`
  - Fatos: `fct_pedidos`, `fct_itens_pedido`, `fct_sessoes_web`, `fct_marketing_diario`
  - Agregados: `agg_rfm_cliente`, `agg_coorte_retencao`
  - Segurança: `sec_acesso_regional`
- Semântica: UC Metric Views `mv_vendas`, `mv_logistica`, `mv_clientes`, `mv_funil_marketing`

## Consumo
- Databricks: AI/BI Dashboard "Data Health" (pipeline, qualidade, custo, negócio) + Genie Space
- Power BI: 5 páginas (Executivo, Produtos, Clientes, Logística, Sellers), RLS regional + seller, versionado como `.pbip`
- Claude: página HTML de funil web e marketing (ROAS, CAC, coortes) via SQL Statement Execution API
- Chatbot Claude com tool use (`consultar_metricas` sobre as metric views, sem SQL livre) + avaliação comparando com Genie

## CI/CD
Databricks Asset Bundles (`databricks.yml` na raiz de `databricks/`) + GitHub Actions. Alvos `dev` (pulso_dev) e `prd` (pulso_prd).

## Estrutura do repositório
```
databricks/      bundle (databricks.yml), resources/*.yml, src/ (00_setup, 10_bronze, 20_silver, ...)
powerbi/         projeto .pbip
app-claude/      chatbot + dashboard HTML
data-generator/  scripts Python dos dados sintéticos
docs/            arquitetura, decisões, blueprint original
```
- Setup do Unity Catalog versionado em `databricks/src/00_setup/unity_catalog.sql` (job `pulso_setup_unity_catalog`)
- Catálogo nunca fixo no código: usar a variável do bundle `${var.catalogo}`

## Roadmap (6 semanas)
1. Fundação (repo, CLI, UC, bundle)
2. Bronze/Silver
3. Gold
4. Semântica + Dashboard/Genie no Databricks
5. Power BI
6. Claude + entrega (README, vídeo, post)

## Como trabalhar neste repo
- CLI: usar sempre o perfil `pulso-dev` (`--profile pulso-dev` ou `DATABRICKS_CONFIG_PROFILE=pulso-dev`)
- Antes de deploy: `databricks bundle validate -t dev`, depois `databricks bundle deploy -t dev`
- Nunca fazer deploy em `prd` sem pedido explícito
- Nunca gravar tokens, hosts privados ou `.databrickscfg` no repositório
- SQL em Databricks SQL; nomes de tabelas e colunas em português, snake_case
- Comentários e documentação em português
