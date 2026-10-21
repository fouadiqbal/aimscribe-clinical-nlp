"""Three-valued source-rule evaluator: True / False / unknown.

Unknown facts are never treated as negative findings. This module is the one
experimental intervention; the baseline receives the same rules without evaluation.
"""
import operator

OPS = {"eq": operator.eq, "lt": operator.lt, "lte": operator.le,
       "gt": operator.gt, "gte": operator.ge, "contains": lambda a, b: b in a}


def evaluate_rule(rule, patient):
    if rule is None:
        return True, []
    if "field" in rule:
        field = rule["field"]
        actual = patient.get(field)
        if actual is None or actual == "":
            return None, [field]
        expected = rule["value"]
        # A string 'false' is not a safe substitute for a boolean finding.
        if isinstance(expected, bool) and not isinstance(actual, bool):
            return None, [field]
        if isinstance(expected, (int,float)) and not isinstance(expected,bool):
            if not isinstance(actual,(int,float)) or isinstance(actual,bool):
                return None, [field]
        try:
            return OPS[rule["op"]](actual, expected), []
        except (TypeError, KeyError):
            return None, [field]
    if "not" in rule:
        value, missing = evaluate_rule(rule["not"], patient)
        return (None if value is None else not value), missing
    key = "all" if "all" in rule else "any" if "any" in rule else "rules"
    results = [evaluate_rule(r, patient) for r in rule[key]]
    values = [v for v, _ in results]
    missing = sorted({m for _, fields in results for m in fields})
    if key == "all":
        value = False if False in values else None if None in values else True
    elif key == "any":
        value = True if True in values else None if None in values else False
    else:
        threshold = rule["at_least"]
        yes, unknown = values.count(True), values.count(None)
        value = True if yes >= threshold else False if yes + unknown < threshold else None
    # Do not demand irrelevant findings after a branch is already conclusive.
    return value, missing if value is None else []


def check_card(card, patient):
    value, unknown = evaluate_rule(card.get("decision_rule"), patient)
    missing = sorted(set(unknown + [k for k in card["required_fields"] if patient.get(k) is None or patient.get(k) == ""]))
    status = "excluded" if value is False else "needs_info" if value is None or missing else "applicable"
    reasons = ["A source-supported prerequisite is contradicted."] if value is False else []
    if status == "needs_info":
        reasons.append("Clarify: " + ", ".join(missing))
    return {"status": status, "missing_fields": missing, "reasons": reasons}
