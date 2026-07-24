from app.services.static_analysis import StaticAnalyzer


def test_simple_function_has_complexity_one():
    report = StaticAnalyzer().analyze("def add(a, b):\n    return a + b\n")
    assert report.function_count == 1
    assert report.functions[0].cyclomatic_complexity == 1
    assert report.naming_violations == []
    assert report.quality_score == 100.0


def test_branches_increase_complexity():
    code = (
        "def check(x):\n"
        "    if x > 0:\n"
        "        if x > 10:\n"
        "            return 'big'\n"
        "        return 'small'\n"
        "    return 'negative'\n"
    )
    report = StaticAnalyzer().analyze(code)
    assert report.functions[0].cyclomatic_complexity == 3


def test_bad_naming_is_flagged():
    code = "def BadFunctionName():\n    pass\n\n\nclass lowercase_class:\n    pass\n"
    report = StaticAnalyzer().analyze(code)
    kinds = {(v.kind, v.name) for v in report.naming_violations}
    assert ("function", "BadFunctionName") in kinds
    assert ("class", "lowercase_class") in kinds


def test_unused_variable_is_detected():
    code = "def f():\n    unused = 1\n    return 2\n"
    report = StaticAnalyzer().analyze(code)
    assert len(report.unused_variables) == 1
    assert report.unused_variables[0].name == "unused"
    assert report.unused_variables[0].scope == "f"


def test_used_variable_is_not_flagged():
    code = "def f():\n    total = 1\n    return total\n"
    report = StaticAnalyzer().analyze(code)
    assert report.unused_variables == []


def test_syntax_error_returns_zero_score():
    report = StaticAnalyzer().analyze("def f(:\n    pass")
    assert report.syntax_error is not None
    assert report.quality_score == 0.0


def test_quality_score_drops_with_more_issues():
    clean = StaticAnalyzer().analyze("def add(a, b):\n    return a + b\n")
    messy_code = (
        "def BadName(x, y):\n"
        "    unused_one = 1\n"
        "    unused_two = 2\n"
        "    if x:\n"
        "        if y:\n"
        "            return 1\n"
        "    return 0\n"
    )
    messy = StaticAnalyzer().analyze(messy_code)
    assert messy.quality_score < clean.quality_score
