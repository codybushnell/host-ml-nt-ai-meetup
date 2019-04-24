.PHONY: run_image_locally

AML_IMAGE_NAME = meetup-utilization
AML_IMAGE_VERSION = 6

run_image_locally:
	@echo "Logging into ACR."
	az acr login --name $(AML_CONTAINER_REGISTRY)
	@echo "Pulling and running the image."
	docker run -d -p 5001:5001 $(AML_CONTAINER_REGISTRY).azurecr.io/$(AML_IMAGE_NAME):$(AML_IMAGE_VERSION)

upload_to_databricks:
	databricks workspace import -l PYTHON -o azure_ml_tutorial/train_model_databricks.py /dev/nt-ai-meetup/train_model_databricks.py
