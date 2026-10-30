# Databricks notebook source
# MAGIC %md
# MAGIC # Download do Olist (Kaggle)
# MAGIC Baixa o dataset `olistbr/brazilian-ecommerce` pela API do Kaggle e guarda os CSVs originais
# MAGIC em `/Volumes/<catalogo>/landing/raw/_fonte/olist/` (staging, fora do alcance do Auto Loader).
# MAGIC
# MAGIC O token fica no secret scope `pulso`, chave `kaggle_api_token`. Se os arquivos já existem, não baixa de novo
# MAGIC (a não ser com `forcar = true`).

# COMMAND ----------

# MAGIC %pip install -q kaggle

# COMMAND ----------

dbutils.widgets.text("catalogo", "pulso_dev")
dbutils.widgets.dropdown("forcar", "false", ["false", "true"])

catalogo = dbutils.widgets.get("catalogo")
forcar = dbutils.widgets.get("forcar") == "true"

DATASET = "olistbr/brazilian-ecommerce"
DESTINO = f"/Volumes/{catalogo}/landing/raw/_fonte/olist"

# Os 9 arquivos esperados do dataset
ARQUIVOS = [
    "olist_customers_dataset.csv",
    "olist_geolocation_dataset.csv",
    "olist_order_items_dataset.csv",
    "olist_order_payments_dataset.csv",
    "olist_order_reviews_dataset.csv",
    "olist_orders_dataset.csv",
    "olist_products_dataset.csv",
    "olist_sellers_dataset.csv",
    "product_category_name_translation.csv",
]

# COMMAND ----------

import os
import shutil
import subprocess
import tempfile

os.makedirs(DESTINO, exist_ok=True)
faltando = [a for a in ARQUIVOS if not os.path.exists(f"{DESTINO}/{a}")]

if not faltando and not forcar:
    print(f"Arquivos já presentes em {DESTINO}; nada a fazer.")
else:
    os.environ["KAGGLE_API_TOKEN"] = dbutils.secrets.get("pulso", "kaggle_api_token")
    tmp = tempfile.mkdtemp(prefix="olist_")
    subprocess.run(["kaggle", "datasets", "download", DATASET, "-p", tmp, "--unzip", "-q"], check=True)

    baixados = set(os.listdir(tmp))
    ausentes = set(ARQUIVOS) - baixados
    if ausentes:
        raise RuntimeError(f"Arquivos ausentes no download: {sorted(ausentes)}")

    for arquivo in ARQUIVOS:
        shutil.copy(f"{tmp}/{arquivo}", f"{DESTINO}/{arquivo}")
    shutil.rmtree(tmp)
    print(f"{len(ARQUIVOS)} arquivos copiados para {DESTINO}")

# COMMAND ----------

display(dbutils.fs.ls(DESTINO))
