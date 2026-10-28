# Pulso Commerce · web_analytics

> 🇧🇷 [Versão em português](README.md)

End-to-end lakehouse for a Brazilian e-commerce company, built on **Databricks** and consumed by **Power BI**, **AI/BI Dashboard + Genie** and a **Claude-built dashboard and chatbot**.

**Business question:** where are we gaining and losing revenue — in the funnel, the product, the seller or the delivery?

> 🚧 Work in progress. Analytics Engineering portfolio project, built in parts.

## Architecture

```
Sources (Olist + synthetic web) → landing (Volume) → Bronze → Silver → Gold (star schema)
  → Semantic (UC Metric Views) → Power BI (RLS) · AI/BI Dashboard + Genie · Claude (HTML + chatbot)
```

- **Data:** [Olist Brazilian E-commerce](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce) (~100k orders, 2016–2018) + synthetic clickstream and media spend
- **Governance:** Unity Catalog with `pulso_dev` / `pulso_prd` catalogs and one schema per layer
- **Pipeline:** Lakeflow Declarative Pipelines (Auto Loader, expectations)
- **CI/CD:** Databricks Asset Bundles + GitHub Actions

Table and column names are in Portuguese (snake_case), matching the business domain.

## Progress

- [x] Part 1 — Foundation (repository, Unity Catalog, bundle)
- [ ] Part 2 — Olist ingestion
- [ ] Part 3 — Bronze
- [ ] Part 4 — Silver
- [ ] Part 5 — Synthetic data
- [ ] Part 6 — Gold: dimensions and facts
- [ ] Part 7 — Gold: aggregates and security
- [ ] Part 8 — Semantic layer
- [ ] Part 9 — AI/BI Dashboard, Genie and Job
- [ ] Part 10 — Power BI
- [ ] Part 11 — Claude dashboard and chatbot
- [ ] Part 12 — CI/CD and delivery

## How to run

```bash
cd databricks
databricks bundle validate -t dev
databricks bundle deploy -t dev
databricks bundle run setup_unity_catalog -t dev
```

---
*Pulso Commerce is a fictional name. Base dataset: Olist Brazilian E-commerce Public Dataset (Kaggle).*
