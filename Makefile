.PHONY: run_image_locally

AML_IMAGE_NAME = meetup-utilization
AML_IMAGE_VERSION = 6

run_image_locally:
	@echo "Logging into ACR."
	az acr login --name $(AML_CONTAINER_REGISTRY)
	@echo "Pulling and running the image."
	docker run -d -p 5001:5001 $(AML_CONTAINER_REGISTRY).azurecr.io/$(AML_IMAGE_NAME):$(AML_IMAGE_VERSION)

test_endpoint:
	curl -X POST \
		http://localhost:5001/score \
		-H 'Content-Type: application/json' \
		-H 'Postman-Token: 8e8dc46d-a4e7-4a15-a930-659ff72ebee5' \
		-H 'cache-control: no-cache' \
		-d '{"data":{"day": "2019-04-24T14:32:58.879285","floor":15}}'

upload_to_databricks:
	databricks workspace import -l PYTHON -o azure_ml_tutorial/train_model_databricks.py /dev/nt-ai-meetup/train_model_databricks.py
