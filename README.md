## CBRE Host ML - Meetup Presentation
### North Texas AI Meetup - April 24th, 2019

### Agenda
1. Brief intro CBRE Host
2. Why we use azure
3. What is azure ml?
4. What is automl?
5. What problems does automl solve?
6. Parallelism
7. Databricks

### Code?

Clone the repo
```bash
git clone
```

Build the conda environment

```bash
conda env create -f environment.yml
```

Get some data

```bash
download_data
```

Do some quick viz

```bash
visualize
```

Engineer some features

```bash
build_features
```

Run automl job to get a baseline model

```bash
find_best_model
```

Register the best model from automl as an Azureml Model

```bash
register_model
```

Create docker image to house the model

```bash
create_image
```

Deploy the container as an Azure container instance

```bash
deploy_image
```