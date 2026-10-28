Blueprint: Pulso Commerce (Task 1)

Mockup publicado: https://claude.ai/artifact/Ju5K4Rsfgaup5SgZH7ETTe

Decisões
Nome do projeto: Pulso Commerce (fictício)
Dataset base: Olist Brazilian E-commerce (Kaggle, ~100 mil pedidos, 2016–2018, 9 tabelas)
Dados web sintéticos (clickstream + investimento em mídia) gerados em Python e ligados aos pedidos reais
Unity Catalog: catálogos pulso_dev / pulso_prd; schemas landing, bronze, silver, gold, semantic, ops
Pipeline: Lakeflow Declarative Pipelines (Auto Loader → expectations no Silver → star schema no Gold)
Gold: dim_cliente, dim_seller (SCD2), dim_produto, dim_data, dim_geografia, dim_canal; fct_pedidos, fct_itens_pedido, fct_sessoes_web, fct_marketing_diario; agg_rfm_cliente, agg_coorte_retencao; sec_acesso_regional
Semântica: UC Metric Views mv_vendas, mv_logistica, mv_clientes, mv_funil_marketing
Consumo:
Databricks AI/BI Dashboard "Data Health" (pipeline, qualidade, custo, negócio) + Genie Space
Power BI: 5 páginas (Executivo, Produtos, Clientes, Logística, Sellers), RLS regional + seller, .pbip no Git
Lovable/Claude: app de funil web e marketing (ROAS, CAC, coortes) via SQL Statement Execution API
Chatbot Claude com tool use (consultar_metricas sobre metric views, sem SQL livre) + avaliação comparando com Genie
CI/CD: Databricks Asset Bundles + GitHub Actions
Roadmap: 6 semanas (Fundação → Bronze/Silver → Gold → Semântica+Databricks → Power BI → Lovable/Claude+entrega)