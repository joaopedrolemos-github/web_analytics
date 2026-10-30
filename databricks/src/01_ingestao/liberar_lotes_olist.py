# Databricks notebook source
# MAGIC %md
# MAGIC # Liberação de lotes do Olist (chegada simulada)
# MAGIC Reproduz o histórico do Olist como se os arquivos chegassem dia a dia no landing.
# MAGIC
# MAGIC - Origem: CSVs originais em `raw/_fonte/olist/`
# MAGIC - Destino: `raw/olist/<tabela>/dt_lote=AAAA-MM-DD/part-*.csv` (lido pelo Auto Loader no Bronze)
# MAGIC - Primeira execução: libera tudo até `data_corte_inicial`
# MAGIC - Execuções seguintes: libera os próximos `dias_por_execucao` dias
# MAGIC - Controle em `ops.controle_lotes_olist` (um registro por tabela × lote), o que torna a liberação idempotente
# MAGIC
# MAGIC Datas de referência: pedidos, itens, pagamentos e clientes pela data da compra; reviews pela data de criação.
# MAGIC Cadastros (sellers, produtos, geolocalização, tradução de categorias) entram uma vez, no primeiro lote.
# MAGIC
# MAGIC Simplificação assumida: o pedido chega já com o status final (não há CDC de status).

# COMMAND ----------

dbutils.widgets.text("catalogo", "pulso_dev")
dbutils.widgets.text("data_corte_inicial", "2018-06-30")
dbutils.widgets.text("dias_por_execucao", "1")

catalogo = dbutils.widgets.get("catalogo")
data_corte_inicial = dbutils.widgets.get("data_corte_inicial")
dias_por_execucao = int(dbutils.widgets.get("dias_por_execucao"))

FONTE = f"/Volumes/{catalogo}/landing/raw/_fonte/olist"
DESTINO = f"/Volumes/{catalogo}/landing/raw/olist"
CONTROLE = f"{catalogo}.ops.controle_lotes_olist"

# Mesmo dialeto de CSV na leitura e na escrita: aspas duplas escapadas por aspas duplas
# e campos com quebra de linha (comentários das reviews)
OPCOES_CSV = {"header": "true", "multiLine": "true", "quote": '"', "escape": '"'}

# COMMAND ----------

from pyspark.sql import functions as F

spark.sql(f"""
  CREATE TABLE IF NOT EXISTS {CONTROLE} (
    tabela        STRING    COMMENT 'Tabela do Olist liberada',
    dt_lote       DATE      COMMENT 'Data do lote (partição dt_lote no landing)',
    qt_linhas     BIGINT    COMMENT 'Linhas gravadas no lote',
    dt_liberacao  TIMESTAMP COMMENT 'Momento em que o lote foi gravado no landing'
  )
  COMMENT 'Controle da chegada simulada dos arquivos do Olist no landing'
""")

def ler_fonte(arquivo):
    return spark.read.options(**OPCOES_CSV).csv(f"{FONTE}/{arquivo}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Janela a liberar

# COMMAND ----------

ultimo_lote = spark.sql(f"SELECT max(dt_lote) FROM {CONTROLE} WHERE tabela = 'orders'").first()[0]

if ultimo_lote is None:
    primeira_carga = True
    dt_fim = spark.sql(f"SELECT DATE'{data_corte_inicial}'").first()[0]
else:
    primeira_carga = False
    dt_fim = spark.sql(f"SELECT date_add(DATE'{ultimo_lote}', {dias_por_execucao})").first()[0]

print(f"Primeira carga: {primeira_carga} | último lote: {ultimo_lote} | liberar até: {dt_fim}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Tabelas com data (fatiadas por dia)

# COMMAND ----------

orders = ler_fonte("olist_orders_dataset.csv")
dt_pedido = orders.select("order_id", "customer_id", F.to_date("order_purchase_timestamp").alias("dt_lote"))

# Cada tabela recebe a coluna dt_lote, que vira a partição no landing
tabelas_com_data = {
    "orders": orders.withColumn("dt_lote", F.to_date("order_purchase_timestamp")),
    "order_items": ler_fonte("olist_order_items_dataset.csv")
        .join(dt_pedido.select("order_id", "dt_lote"), "order_id"),
    "order_payments": ler_fonte("olist_order_payments_dataset.csv")
        .join(dt_pedido.select("order_id", "dt_lote"), "order_id"),
    # No Olist, customer_id é gerado por pedido; o cliente "chega" junto com o pedido
    "customers": ler_fonte("olist_customers_dataset.csv")
        .join(dt_pedido.select("customer_id", "dt_lote"), "customer_id"),
    "order_reviews": ler_fonte("olist_order_reviews_dataset.csv")
        .withColumn("dt_lote", F.to_date("review_creation_date")),
}

def ultimo_lote_da_tabela(tabela):
    return spark.sql(f"SELECT max(dt_lote) FROM {CONTROLE} WHERE tabela = '{tabela}'").first()[0]

def gravar(tabela, df):
    """Grava um arquivo por dt_lote no landing e registra o controle."""
    contagem = df.groupBy("dt_lote").count().collect()
    if not contagem:
        print(f"{tabela}: nada novo")
        return
    (df.repartition("dt_lote")
       .write.mode("append")
       .partitionBy("dt_lote")
       .options(**OPCOES_CSV)
       .csv(f"{DESTINO}/{tabela}"))
    linhas = [(tabela, r["dt_lote"], r["count"]) for r in contagem]
    (spark.createDataFrame(linhas, "tabela STRING, dt_lote DATE, qt_linhas BIGINT")
       .withColumn("dt_liberacao", F.current_timestamp())
       .write.mode("append").saveAsTable(CONTROLE))
    print(f"{tabela}: {sum(r['count'] for r in contagem):,} linhas em {len(contagem)} lotes")

# COMMAND ----------

# "orders" por último: é o marcador da janela; se algo falhar antes, a próxima execução retoma
for tabela in ["order_items", "order_payments", "customers", "order_reviews", "orders"]:
    df = tabelas_com_data[tabela].filter(F.col("dt_lote").isNotNull() & (F.col("dt_lote") <= F.lit(dt_fim)))
    ultimo = ultimo_lote_da_tabela(tabela)
    if ultimo is not None:
        df = df.filter(F.col("dt_lote") > F.lit(ultimo))
    gravar(tabela, df)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Cadastros (carga única no primeiro lote)

# COMMAND ----------

cadastros = {
    "sellers": "olist_sellers_dataset.csv",
    "products": "olist_products_dataset.csv",
    "geolocation": "olist_geolocation_dataset.csv",
    "product_category_name_translation": "product_category_name_translation.csv",
}

dt_cadastro = spark.sql(f"SELECT min(dt_lote) FROM {CONTROLE} WHERE tabela = 'orders'").first()[0]

for tabela, arquivo in cadastros.items():
    if ultimo_lote_da_tabela(tabela) is None:
        gravar(tabela, ler_fonte(arquivo).withColumn("dt_lote", F.lit(dt_cadastro)))

# COMMAND ----------

display(spark.sql(f"""
  SELECT tabela, min(dt_lote) AS primeiro_lote, max(dt_lote) AS ultimo_lote,
         count(*) AS qt_lotes, sum(qt_linhas) AS qt_linhas
  FROM {CONTROLE}
  GROUP BY tabela
  ORDER BY tabela
"""))
