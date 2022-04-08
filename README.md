# Semantic Search: Backend, Preparation and Embedding
## Content
The content of the package is in the following
* data
* database enrichment
* elasticsearch and kibana
* utils

In the folder ./data every script for data cleaning, extraction and ingestion is included. Additionally there are different 
databases in the datasets directory. Configurations has to be made to ingest a new dataset and a running elasticsearch instance 
is needed.

In the folder ./database_enrichment are script to add vector for word or sentence embeddings to a elasticsearch index. 
There are a few configurations and a running elasticsearch instance needed.

In the directory ./docker is a docker setup for elasticsearch and kibana. Just use 
```bash
docker-compose up
```
in the terminal (inside the directory) to start a elasticsearch and kibana instance.

In the directory ./utils are helpful script to communicate with elasticsearch via python, like requests, creating of 
new indices or add new index templates. In the templates folder are the example templates used for my search engine.
Please ignore the tests_and_old_scripts folder, its only for prototypes and will be removed after the project is finished.

### Note
Needed for using spacy models:
Run this once
``` bash 
python -m spacy download en
```
to download the correct spacy model

### Elasticsearch
``` 
sudo chmod 777 elasticsearch/data
```
The first 'docker-compose up' creates a data folder where the container mirrors the databases in.
The folder is only usable for root, so the first start fails. You have to run this command after the first fail 
and run 'docker-compose up' again. 
