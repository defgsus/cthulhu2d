import datetime
import json

from pymunk import Vec2d

from elasticsearch import ElasticsearchException, NotFoundError
from elasticsearch.helpers import bulk

from .client import get_elastic_client


class EsExporterBase:
    """
    Base class helper to export stuff to elasticsearch.

    Derive from class and define class attributes:
        INDEX_NAME: str, name of index
        MAPPINGS: dict, the mapping definition for the index

    And optionally override:
        transform_object_data()

    """

    INDEX_NAME = None
    MAPPINGS = None

    def __init__(self, client=None):
        for required_attribute in ("INDEX_NAME", "MAPPINGS"):
            if not getattr(self, required_attribute, None):
                raise ValueError(f"Need to define class attribute {self.__class__.__name__}.{required_attribute}")
        self.client = client or get_elastic_client()

    def index_name(self):
        return self.INDEX_NAME

    def transform_object_data(self, data):
        """Override this to transform each object's data for elasticsearch"""
        return data

    def update_index(self):
        """
        Create the index or update changes to the mapping
        :return:
        """
        try:
            self.client.indices.get_mapping(index=self.index_name())
            self.client.indices.put_mapping(index=self.index_name(), body=self.MAPPINGS)
        except NotFoundError:
            self.client.indices.create(index=self.index_name(), body=self.get_index_params())

    def export_list(self, object_list, bulk_size=10000):
        """
        Export a list of objects
        :param object_list: list of dict
        :return: dict, response of elasticsearch bulk call
        """
        bulk_actions = []

        for object_data in object_list:

            object_data = self.transform_object_data(object_data)
            object_data = self.make_json_compatible(object_data)

            bulk_actions.append(
                {
                    "_index": self.index_name(),
                    "_source": object_data,
                }
            )

            if len(bulk_actions) >= bulk_size:
                bulk(self.client, bulk_actions)
                bulk_actions = []

        if bulk_actions:
            return bulk(self.client, bulk_actions)

    def get_index_params(self):
        return {
            "mappings": self.MAPPINGS
        }
