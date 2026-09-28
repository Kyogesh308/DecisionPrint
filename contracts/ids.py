def make_decision_id(project_id: str, seq: int) -> str:
    return f"DEC-{project_id.upper()}-{seq:03d}"

def make_outcome_id(project_id: str, seq: int) -> str:
    return f"OUT-{project_id.upper()}-{seq:03d}"
