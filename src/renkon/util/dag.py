from __future__ import annotations

from collections.abc import Iterable
from typing import Generic, TypeVar

T_ = TypeVar("T_")


class DAG(Generic[T_]):
    """
    Generic append-only doubly-linked directed acyclic graph implementation.

    This is not a general purpose graph, it is specifically designed to
    be used in the Reactor for job scheduling. Therefore:

      - Adding edges is only allowed together with a new node.
        - Edges cannot be added between existing nodes.
      - Adding edges is only allowed if it does not create a cycle.
      - Removing nodes is not allowed.
      - Arrows are directed from dependencies to dependents.

    """

    _nodes: list[T_]
    _roots: list[int]
    _fwd_edges: dict[int, set[int]]
    _rev_edges: dict[int, set[int]]

    def __init__(self) -> None:
        self._nodes = []
        self._roots = []
        self._fwd_edges = {}
        self._rev_edges = {}

    def __len__(self) -> int:
        return len(self._nodes)

    def add_node(self, node: T_, dependencies: Iterable[int]) -> int:
        """
        Add a new node to the graph.

        :param node: The node to add.
        :param dependencies: The indices of the nodes that this node depends on.
        :return: The index of the new node.
        """
        node_index = len(self._nodes)
        self._nodes.append(node)
        self._fwd_edges[node_index] = set()
        self._rev_edges[node_index] = set()
        for dependency in dependencies:
            self._fwd_edges[dependency].add(node_index)
            self._rev_edges[node_index].add(dependency)
        if not dependencies:
            self._roots.append(node_index)
        return node_index

    def get_node(self, node_index: int) -> T_:
        """
        Get a node from the graph.

        :param node_index: The index of the node to get.
        :return: The node.
        """
        return self._nodes[node_index]

    def get_roots(self) -> set[int]:
        """
        Get the indices of the root nodes in the graph.

        :return: The indices of the root nodes.
        """
        return set(self._roots)

    def get_dependencies(self, node_index: int) -> set[int]:
        """
        Get the indices of the nodes that a node depends on.

        :param node_index: The index of the node.
        :return: The indices of the nodes that the node depends on.
        """
        return self._rev_edges[node_index]

    def get_dependents(self, node_index: int) -> set[int]:
        """
        Get the indices of the nodes that depend on a node.

        :param node_index: The index of the node.
        :return: The indices of the nodes that depend on the node.
        """
        return self._fwd_edges[node_index]

    def get_descendants(self, node_index: int) -> set[int]:
        """
        Get the indices of the nodes that are descendants of a node.

        :param node_index: The index of the node.
        :return: The indices of the nodes that are descendants of the node.
        """
        descendants = set()
        stack = [node_index]
        while stack:
            idx = stack.pop()
            descendants.add(idx)
            stack.extend(self._fwd_edges[idx])
        descendants.remove(node_index)
        return descendants
