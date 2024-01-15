import subprocess
import docker
from elasticsearch import Elasticsearch


# Start docker image
def start_es_docker(container_name="es_search"):
    """
    Start a docker container for ElasticSearch if one isn't already up.
    :param container_name:
    :return: None
    """
    localhost = "http://localhost:9200"
    if is_docker_container_running(container_name):
        print("Docker is already running")
    else:
        print("Docker container not found. Starting Docker container...")
        subprocess.Popen('docker run -d --rm -p 9200:9200 -p 9300:9300 '
                         '--name es_search '
                         '-e "xpack.security.enabled=false" '
                         '-e "discovery.type=single-node" '
                         'docker.elastic.co/elasticsearch/elasticsearch:8.3.3')
        print("Starting ElasticSearch docker container...")
    es = Elasticsearch(localhost)
    return es, localhost


def is_docker_container_running(container_name="es_search"):
    """
    Check if a docker container is already running
    :param container_name:
    :return: True or False
    """
    client = docker.from_env()
    try:
        container = client.containers.get(container_name)
        return container.status == "running"
    except docker.errors.NotFound:
        return False


def stop_docker_container(container_name="es_search"):
    """
    Stop a docker container with a given name
    :param container_name:
    :return: None
    """
    if is_docker_container_running(container_name):
        docker.from_env().containers.get(container_name).stop()


def get_all_docker() -> list:
    """
    Return all running docker container
    :return: A list of running containers
    """
    client = docker.from_env()
    containers_info = []

    for container in client.containers.list():
        container_info = {
            'Name': container.name,
            'Type': container.image.attrs['RepoTags'][
                0] if container.image.attrs.get('RepoTags') else 'Unknown'
        }
        containers_info.append(container_info)

    return containers_info
