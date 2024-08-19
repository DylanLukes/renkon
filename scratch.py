# pyright: strict

from typing import Annotated


class _Widget:
    pass


type Widget = Annotated[_Widget, "yada yada yada"]

w = Widget()  # 2 typing errors

# Example 1
# ❯ PYRIGHT_PYTHON_FORCE_VERSION=latest pyright scratch.py
# .../scratch.py
#   .../scratch.py:11:1 - error: Type of "w" is unknown (reportUnknownVariableType)
#   .../scratch.py:11:5 - error: Object of type "TypeAliasType" is not callable
#     Attribute "__call__" is unknown (reportCallIssue)
# 2 errors, 0 warnings, 0 informations

isinstance(w, Widget)  # 4 typing errors

# Example 2
#
#   .../scratch.py:26:15 - error: Argument of type "Widget" cannot be assigned to parameter "class_or_tuple" of type "_ClassInfo" in function "isinstance"
#     Type "TypeAliasType" is incompatible with type "_ClassInfo"
#       "TypeAliasType" is incompatible with "type"
#       "TypeAliasType" is incompatible with "UnionType"
#       "TypeAliasType" is incompatible with "tuple[_ClassInfo, ...]" (reportArgumentType)
#
#   .../scratch.py:26:15 - error: Second argument to "isinstance" must be a class or tuple of classes
#     Type alias created with "type" statement cannot be used with instance and class checks (reportArgumentType)

def make_widget(cls: type[Widget]):
    return cls()

w = make_widget(Widget) # 1 typing error

# Example 3
#
#   .../scratch.py:38:17 - error: Argument of type "Widget" cannot be assigned to parameter "cls" of type "type[_Widget]" in function "make_widget"
#     Type "TypeAliasType" is incompatible with type "type[_Widget]" (reportArgumentType)
