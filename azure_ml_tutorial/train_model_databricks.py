"""Module for training the utilization prediction model."""
import logging
import uuid

import azureml.dataprep as dprep
from azureml.core.experiment import Experiment
from azureml.core.workspace import Workspace
from azureml.train.automl import AutoMLConfig

target = "utilization"
ws = Workspace(
    workspace_name=dbutils.secrets.get("azureml", "AML_WORKSPACE_NAME"),  # noqa
    subscription_id=dbutils.secrets.get("azureml", "AML_SUBSCRIPTION_ID"),  # noqa
    resource_group=dbutils.secrets.get("azureml", "AML_RESOURCE_GROUP"),  # noqa
)
ds = ws.get_default_datastore()

x = dprep.read_parquet_file(
    ds.path('model_data_x.parquet')
)
y = dprep.read_parquet_file(
    ds.path('model_data_y.parquet')
).to_long(
    dprep.ColumnSelector(
        term='.*',
        use_regex=True
    )
)

project_folder = './automl'
automl_config = AutoMLConfig(
    task="regression",
    iteration_timeout_minutes=10,
    iterations=10,
    primary_metric="r2_score",
    n_cross_validations=5,
    debug_log="automl.log",
    verbosity=logging.INFO,
    spark_context=sc,  # noqa
    whitelist_models=[
        "GradientBoosting",
        "DecisionTree",
        "RandomForest",
        "ExtremeRandomTrees",
        "LightGBM",
    ],
    blacklist_models=[
        "ensemble"
    ],
    X=x,
    y=y,
    path=project_folder,
)


experiment = Experiment(ws, "host-ml-nt-ai-meetup")

db_run = experiment.submit(automl_config, show_output=True)

sub_runs = list(db_run.get_children())

best_run = None
best_score = 0

for sub_run in sub_runs:
    props = sub_run.get_properties()
    if props["run_algorithm"] != "Ensemble":
        if float(props["score"]) > best_score:
            best_run = sub_run

model_name = "Automl{}".format(str(uuid.uuid4()).replace("-", ""))[:20]
best_run.register_model(model_name=model_name)
# best_run, fitted_model = local_run.get_output()
# local_run.register_model(
#     description="automl meetup best model"
# )
print("Model name is {}".format(model_name))
# db_run.register_model(
#     description="databricks automl meetup best model"
# )
