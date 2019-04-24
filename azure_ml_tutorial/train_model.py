"""Module for training the utilization prediction model."""
import logging
from os import getenv
import uuid

import click
import pandas as pd
from azureml.core.experiment import Experiment
from azureml.core.workspace import Workspace
from azureml.train.automl import AutoMLConfig

from dotenv import find_dotenv, load_dotenv


@click.command()
@click.option(
    "--data-file", "-f", type=click.Path(exists=True), default="data/model_data.parquet"
)
@click.option("--random-seed", "-r", type=click.INT, default=0)
def train_model(data_file, random_seed):
    """Train the automl model."""
    target = "utilization"
    df = pd.read_parquet(data_file)

    x = df.loc[:, [c for c in df if c != target]].values
    y = df[target].values
    project_folder = "./automl"

    automl_config = AutoMLConfig(
        task="regression",
        iteration_timeout_minutes=10,
        iterations=10,
        primary_metric="spearman_correlation",
        n_cross_validations=5,
        debug_log="automl.log",
        verbosity=logging.INFO,
        whitelist_models=[
            "GradientBoosting",
            "DecisionTree",
            "RandomForest",
            "ExtremeRandomTrees",
            "LightGBM",
        ],
        X=x,
        y=y,
        path=project_folder,
    )

    load_dotenv(find_dotenv())
    ws = Workspace(
        workspace_name=getenv("AML_WORKSPACE_NAME"),
        subscription_id=getenv("AML_SUBSCRIPTION_ID"),
        resource_group=getenv("AML_RESOURCE_GROUP"),
    )
    experiment = Experiment(ws, getenv("AML_EXPERIMENT_NAME"))

    local_run = experiment.submit(automl_config, show_output=True)

    sub_runs = list(local_run.get_children())

    best_run = None
    best_score = 0

    for sub_run in sub_runs:
        props = sub_run.get_properties()
        if props["run_algorithm"] != "Ensemble":
            if float(props["score"]) > best_score:
                best_run = sub_run

    model_name = "Automl{}".format(str(uuid.uuid4()).replace("-", "")[:29])
    best_run.register_model(model_name=model_name)
    # best_run, fitted_model = local_run.get_output()
    # local_run.register_model(
    #     description="automl meetup best model"
    # )
    print("Model name is {}".format(model_name))


if __name__ == "__main__":
    train_model()
