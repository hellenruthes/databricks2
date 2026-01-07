import os
from dotenv import load_dotenv
load_dotenv()


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
    