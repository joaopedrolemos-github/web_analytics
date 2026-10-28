# Pulso Commerce · web_analytics

> 🇬🇧 [English version](README.en.md)

Lakehouse de ponta a ponta para um e-commerce brasileiro, construído no **Databricks** e consumido por **Power BI**, **AI/BI Dashboard + Genie** e um **dashboard/chatbot feito com Claude**.

**Pergunta de negócio:** onde estamos ganhando e perdendo receita — no funil, no produto, no seller ou na entrega?

> 🚧 Em construção. Projeto de portfólio para Analytics Engineering, desenvolvido em partes.

## Arquitetura

```
Fontes (Olist + web sintético) → landing (Volume) → Bronze → Silver → Gold (star schema)
  → Semântica (UC Metric Views) → Power BI (RLS) · AI/BI Dashboard + Genie · Claude (HTML + chatbot)
```

- **Dados:** [Olist Brazilian E-commerce](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce) (~100 mil pedidos, 2016–2018) + clickstream e investimento em mídia sintéticos
- **Governança:** Unity Catalog com catálogos `pulso_dev` / `pulso_prd` e um schema por camada
- **Pipeline:** Lakeflow Declarative Pipelines (Auto Loader, expectations)
- **CI/CD:** Databricks Asset Bundles + GitHub Actions

## Progresso

- [x] Parte 1 — Fundação (repositório, Unity Catalog, bundle)
- [ ] Parte 2 — Ingestão Olist
- [ ] Parte 3 — Bronze
- [ ] Parte 4 — Silver
- [ ] Parte 5 — Dados sintéticos
- [ ] Parte 6 — Gold: dimensões e fatos
- [ ] Parte 7 — Gold: agregados e segurança
- [ ] Parte 8 — Camada semântica
- [ ] Parte 9 — AI/BI Dashboard, Genie e Job
- [ ] Parte 10 — Power BI
- [ ] Parte 11 — Dashboard e chatbot com Claude
- [ ] Parte 12 — CI/CD e entrega

## Como rodar

```bash
cd databricks
databricks bundle validate -t dev
databricks bundle deploy -t dev
databricks bundle run setup_unity_catalog -t dev
```

## Estrutura

```
databricks/      bundle, pipelines, notebooks, SQL das metric views
powerbi/         projeto .pbip
app-claude/      chatbot + dashboard HTML
data-generator/  scripts Python dos dados sintéticos
docs/            arquitetura, decisões, blueprint
```

---
*Pulso Commerce é um nome fictício. Dataset base: Olist Brazilian E-commerce Public Dataset (Kaggle).*
