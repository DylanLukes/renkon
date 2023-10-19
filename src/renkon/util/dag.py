from __future__ import annotations

from collections.abc import Iterable


class DAG[T]:
    """
    Generic append-only doubly-linked directed acyclic graph implementation.

    This is not a general purpose graph, it is specifically designed to
    be used for the TaskGraph. Therefore:

      - Adding edges is only allowed together with a new node.
        - Edges cannot be added between existing nodes.
      - Adding edges is only allowed if it does not create a cycle.
      - Removing nodes is not allowed.
      - Arrows directed from dependencies to dependents.

    """

    nodes: list[T]
    roots: list[int]
    children: dict[int, set[int]]
    parents: dict[int, set[int]]

    def __init__(self) -> None:
        self.nodes = []
        self.roots = []
        self.children = {}
        self.parents = {}

    def __len__(self) -> int:
        return len(self.nodes)

    def add_node(self, node: T, parent_ids: Iterable[int]) -> int:
        """
        Add a new node to the graph.

        :param node: The node to add.
        :param parent_ids: The indices of the nodes that this node depends on.
        :return: The index of the new node.
        """
        node_id = len(self.nodes)
        self.nodes.append(node)

        self.children[node_id] = set()
        self.parents[node_id] = set()

        for parent_id in parent_ids:
            self.children[parent_id].add(node_id)
            self.parents[node_id].add(parent_id)

        if not parent_ids:
            self.roots.append(node_id)

        return node_id

    def get_node(self, node_id: int) -> T:
        """
        Get a node from the graph.

        :param node_id: The index of the node to get.
        :return: The node.
        """
        return self.nodes[node_id]

    def get_roots(self) -> set[int]:
        """
        Get the indices of the root nodes in the graph.

        :return: The indices of the root nodes.
        """
        return set(self.roots)

    def get_parents(self, node_id: int) -> set[int]:
        """
        Get the indices of the nodes that a node depends on.

        :param node_id: The index of the node.
        :return: The indices of the nodes that the node depends on.
        """
        return self.parents[node_id]

    def get_children(self, node_id: int) -> set[int]:
        """
        Get the indices of the nodes that depend on a node.

        :param node_id: The index of the node.
        :return: The indices of the nodes that depend on the node.
        """
        return self.children[node_id]

    def get_descendants(self, node_id: int) -> set[int]:
        """
        Get the indices of the nodes that are descendants of a node.

        :param node_id: The index of the node.
        :return: The indices of the nodes that are descendants of the node.
        """
        descendants: set[int] = set()
        stack = [node_id]

        while stack:
            id_ = stack.pop()
            descendants.add(id_)
            stack.extend(self.children[id_])

        descendants.remove(node_id)
        return descendants
