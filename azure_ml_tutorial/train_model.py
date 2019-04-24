"""Module for training the utilization prediction model."""
import logging
from os import getenv

import click
import pandas as pd
from azureml.core.experiment import Experiment
from azureml.core.workspace import Workspace
from azureml.train.automl import AutoMLConfig

# from sklearn.model_selection import train_test_split
from dotenv import find_dotenv, load_dotenv


@click.command()
@click.option(
    "--data-file", "-f", type=click.Path(exists=True), default="model_data.parquet"
)
@click.option("--random-seed", "-r", type=click.INT, default=0)
def train_model(data_file, random_seed):
    """Train the automl model."""
    target = "utilization"
    df = pd.read_parquet(data_file)

    x = df.loc[:, [c for c in df if c != target]].values
    y = df[target].values
    # x_train, x_test, y_train, y_test = train_test_split(
    #     x, y, test_size=0.3, random_state=223
    # )
    project_folder = "./automl"

    automl_config = AutoMLConfig(
        task="regression",
        iteration_timeout_minutes=10,
        iterations=10,
        primary_metric="spearman_correlation",
        n_cross_validations=5,
        debug_log="automl.log",
        verbosity=logging.INFO,
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
    best_run, fitted_model = local_run.get_output()
    local_run.register_model(
        description="automl meetup best model"
    )
    print("Model name is {}".format(local_run.model_id))


if __name__ == "__main__":
    train_model()
