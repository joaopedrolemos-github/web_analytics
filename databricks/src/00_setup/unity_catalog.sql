-- Databricks notebook source
-- Setup do Unity Catalog do Pulso Commerce.
-- Idempotente: pode rodar quantas vezes quiser.
-- Parâmetro: catalogo (pulso_dev ou pulso_prd), recebido do job do bundle.

-- COMMAND ----------

CREATE WIDGET TEXT catalogo DEFAULT 'pulso_dev';

-- COMMAND ----------

CREATE CATALOG IF NOT EXISTS IDENTIFIER(:catalogo)
  COMMENT 'Pulso Commerce: lakehouse de e-commerce (Olist + dados web sintéticos)';

-- COMMAND ----------

-- Um schema por camada
CREATE SCHEMA IF NOT EXISTS IDENTIFIER(:catalogo || '.landing')
  COMMENT 'Arquivos brutos recebidos (Volume raw): Olist, web e marketing';
CREATE SCHEMA IF NOT EXISTS IDENTIFIER(:catalogo || '.bronze')
  COMMENT 'Cópia fiel das fontes + metadados de ingestão (streaming tables, append-only)';
CREATE SCHEMA IF NOT EXISTS IDENTIFIER(:catalogo || '.silver')
  COMMENT 'Dados limpos, tipados e deduplicados, com expectations de qualidade';
CREATE SCHEMA IF NOT EXISTS IDENTIFIER(:catalogo || '.gold')
  COMMENT 'Modelo dimensional (star schema): dimensões, fatos, agregados e segurança';
CREATE SCHEMA IF NOT EXISTS IDENTIFIER(:catalogo || '.semantic')
  COMMENT 'Camada semântica: metric views e funções para consumo por BI e IA';
CREATE SCHEMA IF NOT EXISTS IDENTIFIER(:catalogo || '.ops')
  COMMENT 'Operação: resultados de qualidade, auditoria, custo e log do chatbot';

-- COMMAND ----------

-- Volume de chegada dos arquivos: /Volumes/<catalogo>/landing/raw/{olist,web,mkt}
CREATE VOLUME IF NOT EXISTS IDENTIFIER(:catalogo || '.landing.raw')
  COMMENT 'Arquivos brutos: olist/, web/, mkt/';
