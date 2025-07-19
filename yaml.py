from typing import Any, Dict

def safe_load(stream: str) -> Dict[str, Any]:
    if hasattr(stream, 'read'):
        content = stream.read()
    else:
        content = stream
    lines = [line.rstrip() for line in content.splitlines() if line.strip()]
    result: Dict[str, Any] = {}
    stack: list[tuple[int, Dict[str, Any]]] = [(0, result)]
    for line in lines:
        indent = len(line) - len(line.lstrip())
        key, _, value = line.lstrip().partition(':')
        key = key.strip()
        value = value.strip()
        while stack and indent < stack[-1][0]:
            stack.pop()
        current = stack[-1][1]
        if value:
            current[key] = value
        else:
            new_dict: Dict[str, Any] = {}
            current[key] = new_dict
            stack.append((indent + 2, new_dict))
    return result
