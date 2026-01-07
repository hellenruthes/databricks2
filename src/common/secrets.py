import os
from dotenv import load_dotenv
load_dotenv()


def get_dbutils():
    """
    Retorna uma instância de dbutils quando em Databricks.
    """
    try:
        from pyspark.sql import SparkSession
        from pyspark.dbutils import DBUtils

        spark = SparkSession.getActiveSession()
        if spark is None:
            return None

        return DBUtils(spark)
    except Exception:
        return None


def get_secret(key: str, scope: str | None = None) -> str:
    """
    Busca segredo no Databricks Secrets (se disponível),
    senão cai para variável de ambiente.
    """
    dbutils = get_dbutils()

    # Databricks
    if dbutils and scope:
        try:
            return dbutils.secrets.get(scope=scope, key=key)
        except Exception as e:
            raise RuntimeError(
                f"Secret '{key}' not found in Databricks scope '{scope}'"
            ) from e

    # Fallback local (.env / env var)
    value = os.getenv(key)
    if value:
        return value

    raise RuntimeError(
        f"Secret '{key}' not found in Databricks or environment variables"
    )

def get_secret(key: str, scope: str | None = None) -> str:
    """
    Retorna segredo do Databricks (se disponível) ou do ambiente local (.env).

    """
    print(key)
    try:
        secret_value = dbutils.secrets.get(scope=scope,
                                          key=key
                                        )
        #secret_value = dbutils.secrets.get(scope="hellendev2", key="openaiapi")
        #print(f'{key} was found')
        return secret_value
    except Exception:
        # Local / fallback
        value = os.getenv(key)
        if not value:
            raise RuntimeError(f"Secret '{key}' not found in env or Databricks")
        return value
    