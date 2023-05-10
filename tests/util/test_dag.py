from renkon.util.dag import DAG


def test_dag_line() -> None:
    d = DAG[str]()
    id_a = d.add_node("a", [])
    id_b = d.add_node("b", [id_a])
    id_c = d.add_node("c", [id_b])
    assert d.get_dependents(id_a) == {id_b}
    assert d.get_dependents(id_b) == {id_c}
    assert d.get_dependents(id_c) == set()


def test_dag_disjoint() -> None:
    d = DAG[str]()
    id_a = d.add_node("a", [])
    id_b = d.add_node("b", [id_a])
    id_c = d.add_node("c", [id_b])

    id_x = d.add_node("x", [])
    id_y = d.add_node("y", [id_x])
    id_z = d.add_node("z", [id_y])

    assert d.get_roots() == {id_a, id_x}

    assert d.get_descendants(id_a) == {id_b, id_c}
    assert d.get_descendants(id_x) == {id_y, id_z}


def test_dag_diamond() -> None:
    d = DAG[str]()
    id_a = d.add_node("a", [])
    id_b = d.add_node("b", [id_a])
    id_c = d.add_node("c", [id_a])
    id_d = d.add_node("d", [id_b, id_c])

    assert d.get_roots() == {id_a}

    assert d.get_descendants(id_a) == {id_b, id_c, id_d}
    assert d.get_descendants(id_b) == {id_d}
    assert d.get_descendants(id_c) == {id_d}
    assert d.get_descendants(id_d) == set()
