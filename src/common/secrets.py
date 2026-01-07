import os
from dotenv import load_dotenv
load_dotenv()


def get_dbutils():
    try:
        from pyspark.sql import SparkSession
        from pyspark.dbutils import DBUtils

        spark = SparkSession.builder.getOrCreate()
        return DBUtils(spark)
    except Exception:
        return None


def get_secret(key: str, scope: str | None = None, env_fallback: bool = True) -> str:
    """
    1) Databricks secret scope (que pode ser backed by Key Vault)
    2) Fallback para env var (local)
    """
    dbutils = get_dbutils()
    if dbutils and scope:
        try:
            return dbutils.secrets.get(scope=scope, key=key)
        except Exception as e:
            # se for Databricks e falhou, eu prefiro falhar "alto" para não mascarar permissão/typo
            raise RuntimeError(f"Failed to read secret '{key}' from scope '{scope}': {e}") from e

    if env_fallback:
        v = os.getenv(key)
        if v:
            return v

    raise RuntimeError(f"Secret '{key}' not found (scope={scope}) and no env fallback.")

    