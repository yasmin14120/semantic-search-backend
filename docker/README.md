# Elastic Search package

![Elastic Stack version](https://img.shields.io/badge/ELK-7.1.1-blue.svg?style=flat)

This package contains the current [ElasticStack][elk-stack], based on the official Docker images from Elastic:

* [ElasticSearch](https://github.com/elastic/elasticsearch-docker)
* [Kibana](https://github.com/elastic/kibana-docker)



## Requirements

1. Install [Docker](https://www.docker.com/community-edition#/download) version **17.05+**
2. Install [Docker Compose](https://docs.docker.com/compose/install/) version **1.6.0+**

By default, the stack exposes the following ports:
* 9200: Elasticsearch HTTP
* 9300: Elasticsearch TCP transport
* 5601: Kibana


## Usage

Start the stack using Docker Compose:

```console
$ docker-compose up
```

You can also run all services in the background (detached mode) by adding the `-d` flag to the above command.

### Credentials

The stack is pre-configured with the following user:

* user: *elastic*
* password: *droxIT2019*

### Troubleshooting

If `docker-compose up` yields the error 

    elasticsearch_1  | [1]: max virtual memory areas vm.max_map_count [65530] is too low, increase to at least [262144]
    
try executing the following command:

	sysctl -w vm.max_map_count=262144

To make these changes permanent, add `vm.max_map_count=262144` to your /etc/sysctl.conf



[elk-stack]: https://www.elastic.co/elk-stack
