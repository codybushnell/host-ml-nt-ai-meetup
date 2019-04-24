"""Module for building the container to host the utilization prediction model."""
from os import chdir, getenv

import click
from azureml.core.image import ContainerImage, Image
from azureml.core.model import Model
from azureml.core.workspace import Workspace
from dotenv import find_dotenv, load_dotenv


@click.command()
def build_image():
    """Build the docker image to hold the model."""
    load_dotenv(find_dotenv())

    chdir("deploy")
    ws = Workspace(
        workspace_name=getenv("AML_WORKSPACE_NAME"),
        subscription_id=getenv("AML_SUBSCRIPTION_ID"),
        resource_group=getenv("AML_RESOURCE_GROUP"),
    )
    model = Model(ws, getenv("AML_MODEL_NAME"))

    image_config = ContainerImage.image_configuration(
        runtime="python",
        execution_script="score.py",
        conda_file="container_conda_env.yml"
    )

    image = Image.create(
        name=getenv("AML_IMAGE_NAME"),
        models=[model],
        image_config=image_config,
        workspace=ws
    )

    image.wait_for_creation(
        show_output=True
    )


if __name__ == "__main__":
    build_image()
