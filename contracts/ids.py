def make_source_id(project_id: str, sequence: int) -> str:
    """Creates a source ID in the format SRC-{PROJECT}-{NNN:03d}."""
    return f"SRC-{project_id.upper()}-{sequence:03d}"


def make_outcome_id(project_id: str, sequence: int) -> str:
    """Creates an outcome ID in the format OUT-{PROJECT}-{NNN:03d}."""
    return f"OUT-{project_id.upper()}-{sequence:03d}"


def make_decision_id(project_id: str, sequence: int) -> str:
    """Creates a decision ID in the format DEC-{PROJECT}-{NNN:03d}."""
    return f"DEC-{project_id.upper()}-{sequence:03d}"
