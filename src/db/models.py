from abc import ABC, abstractmethod
from typing import Optional
from pydantic import BaseModel


class Entity(BaseModel, ABC):
    @abstractmethod
    def compose_merge_query(self):
        pass

    @abstractmethod
    def compose_create_query(self):
        pass


class Node(Entity):
    name: str
    node_type: str
    node_subtype: Optional[str]
    properties: dict[str, str | float | int]

    def compose_merge_query(self):
        pass

    def compose_create_query(self):
        pass


class Edge(Entity):
    first_node: Node
    second_node: Node
    properties: dict[str, str | float | int]

    def compose_merge_query(self):
        pass

    def compose_create_query(self):
        pass

