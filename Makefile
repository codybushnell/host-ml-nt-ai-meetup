.PHONY: run_image_locally test_endpoint upload_to_databricks

AML_IMAGE_NAME = meetup-utilization
AML_IMAGE_VERSION = 8
LOCAL_ENDPOINT_PORT = 5001

run_image_locally:
	@echo "Logging into ACR."
	az acr login --name $(AML_CONTAINER_REGISTRY)
	@echo "Pulling and running the image."
	docker run -d -p $(LOCAL_ENDPOINT_PORT):5001 $(AML_CONTAINER_REGISTRY).azurecr.io/$(AML_IMAGE_NAME):$(AML_IMAGE_VERSION)

test_endpoint:
	curl -X POST \
		http://localhost:$(LOCAL_ENDPOINT_PORT)/score \
		-H 'Content-Type: application/json' \
		-H 'Postman-Token: 8e8dc46d-a4e7-4a15-a930-659ff72ebee5' \
		-H 'cache-control: no-cache' \
		-d '{"data":{"day": "2019-04-24T14:32:58.879285","floor":15}}'

upload_to_databricks:
	databricks workspace import -l PYTHON -o azure_ml_tutorial/train_model_databricks.py /dev/nt-ai-meetup/train_model_databricks.py
