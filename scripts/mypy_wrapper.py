"""
Problem: the following script configuration will not pick up on types
from py.typed dependencies in the main environment.

    [envs.lint.scripts]
    typing = "mypy --install-types --non-interactive {args:.}"

Solution:
    - get the location of the main environment python executable from hatch
    - pass it to mypy as --python-executable

"""
