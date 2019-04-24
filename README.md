## CBRE Host ML - Meetup Presentation Code
### North Texas AI Meetup - April 24th, 2019

### Code

Prerequisites

* conda
* databricks cli
* git
* azure subscription
* azure databricks workspace
* azure machine learning service
* docker

Clone the repo
```bash
git clone https://github.com/cbre360/host-ml-nt-ai-meetup.git
```

Build the conda environment

```bash
conda env create -f environment.yml
```

Activate the environment

```bash
source activate host-ml-nt-ai-meetup
```

Get some data

```bash
get_data
```

Engineer some features

```bash
engineer_features
```

Run automl job to get a baseline model

```bash
train_model
```

Create docker image to house the model

```bash
build_image
```

Test the container

```bash
make
```