import ast
from pathlib import Path


def test_http_routes_do_not_import_infrastructure():
    root = Path(__file__).parents[2]
    source = (root / "src/njinet_agent/presentation/http/api/agent.py").read_text()
    imports = {
        node.module
        for node in ast.walk(ast.parse(source))
        if isinstance(node, ast.ImportFrom)
        and node.module
        and node.module.startswith("njinet_agent.infrastructure.")
    }

    assert imports == set()
