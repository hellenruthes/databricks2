# databricks2
## Activate Virtual Environment
`python3.12 -m venv .venv312`

## Install dependencies
`pip install -U pip`
`pip install .`


pip install -U pip
pip install .

## If running locally and you want to check MLFlow generated on mlruns
`mlflow ui`

mlflow is available on http://127.0.0.1:5000/
In case of you want another port `mlflow ui --port 5001`

### Tips to close MLFlow
✔️ Ctrl + C → When terminal is still open

✔️ lsof + kill → when it got lost

✔️ another port → If you don't want to interrupt

##Show tree
tree -L 4 -I ".venv|__pycache__|*.egg-info|.git"

##
| Tipo de coisa    | Onde fica        | Por quê                                 |
| ---------------- | ---------------- | --------------------------------------- |
| **Job**          | `weekly/jobs/`   | É o *entrypoint* (Databricks roda isso) |
| **Crew**         | `weekly/crews/`  | Orquestra agents + tasks                |
| **Agent**        | `weekly/agents/` | Responsabilidade cognitiva              |
| **Task**         | `weekly/tasks/`  | Prompt / contrato de trabalho           |
| **Utils comuns** | `common/`        | Compartilhado entre domínios            |


cd /Users/hellenruthes/dev/databricks2/src/agents_ai/weekly/jobs
python weekly_job.py \
  --week_of 2026-01-05 \
  --topics "Resources Weekly Used..." \
  --data "" \
  --verbose


  ##On databricks
  python -m venv .venv
source .venv/bin/activate
pip install -U pip build
python -m build


ls dist/
# agents_ia-0.1.0-py3-none-any.whl

databricks fs mkdirs dbfs:/FileStore/wheels
databricks fs cp dist/*.whl dbfs:/FileStore/wheels/ --overwrite

databricks fs mkdirs dbfs:/FileStore/wheels
databricks fs cp dist/weekly_report-0.1.0-py3-none-any.whl \
  dbfs:/FileStore/wheels/weekly_report-0.1.0-py3-none-any.whl \
  --overwrite

databricks fs ls dbfs:/FileStore/wheels