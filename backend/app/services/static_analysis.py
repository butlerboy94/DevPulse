from __future__ import annotations

import ast
import re
from dataclasses import dataclass
from typing import Iterator

_SNAKE_CASE_RE = re.compile(r"^[a-z_][a-z0-9_]*$")
_CONSTANT_RE = re.compile(r"^[A-Z_][A-Z0-9_]*$")
_PASCAL_CASE_RE = re.compile(r"^[A-Z][a-zA-Z0-9]*$")


@dataclass
class FunctionMetrics:
    name: str
    line_number: int
    line_count: int
    cyclomatic_complexity: int


@dataclass
class NamingViolation:
    kind: str  # "function" | "class" | "variable"
    name: str
    line_number: int
    reason: str


@dataclass
class UnusedVariable:
    name: str
    line_number: int
    scope: str  # "module" or the enclosing function's name


@dataclass
class StaticAnalysisReport:
    lines_of_code: int
    function_count: int
    average_cyclomatic_complexity: float
    max_cyclomatic_complexity: int
    functions: list[FunctionMetrics]
    naming_violations: list[NamingViolation]
    unused_variables: list[UnusedVariable]
    quality_score: float
    syntax_error: str | None = None


def _own_body_nodes(node: ast.AST) -> Iterator[ast.AST]:
    """
    Walk every descendant of `node` *except* the insides of nested function
    or class definitions. This lets us measure a function's own complexity
    and local variables without double-counting work that belongs to a
    function defined inside it.
    """
    for child in ast.iter_child_nodes(node):
        yield child
        if not isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            yield from _own_body_nodes(child)


class StaticAnalyzer:
    """
    Reads a piece of Python source code the same way a linter would — not
    by running it, but by turning it into an Abstract Syntax Tree (AST): a
    structured map of every statement and expression in the file. From that
    map we measure how tangled the logic is (cyclomatic complexity), how
    long functions are, whether names follow Python's naming conventions,
    and whether any variable is assigned but never used.
    """

    def analyze(self, source_code: str) -> StaticAnalysisReport:
        try:
            tree = ast.parse(source_code)
        except SyntaxError as exc:
            return StaticAnalysisReport(
                lines_of_code=len(source_code.splitlines()),
                function_count=0,
                average_cyclomatic_complexity=0.0,
                max_cyclomatic_complexity=0,
                functions=[],
                naming_violations=[],
                unused_variables=[],
                quality_score=0.0,
                syntax_error=f"{exc.msg} (line {exc.lineno})",
            )

        functions = self._analyze_functions(tree)
        naming_violations = self._check_naming(tree)
        unused_variables = self._find_unused_variables(tree)

        complexities = [f.cyclomatic_complexity for f in functions] or [self._complexity(tree)]
        avg_complexity = sum(complexities) / len(complexities)

        quality_score = self._score(
            avg_complexity=avg_complexity,
            naming_violation_count=len(naming_violations),
            unused_variable_count=len(unused_variables),
            long_function_count=sum(1 for f in functions if f.line_count > 50),
        )

        non_blank_lines = [line for line in source_code.splitlines() if line.strip()]

        return StaticAnalysisReport(
            lines_of_code=len(non_blank_lines),
            function_count=len(functions),
            average_cyclomatic_complexity=round(avg_complexity, 2),
            max_cyclomatic_complexity=max(complexities),
            functions=functions,
            naming_violations=naming_violations,
            unused_variables=unused_variables,
            quality_score=quality_score,
        )

    # ── metrics ──────────────────────────────────────────────────────────

    def _analyze_functions(self, tree: ast.AST) -> list[FunctionMetrics]:
        functions = []
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                line_count = (node.end_lineno or node.lineno) - node.lineno + 1
                functions.append(
                    FunctionMetrics(
                        name=node.name,
                        line_number=node.lineno,
                        line_count=line_count,
                        cyclomatic_complexity=self._complexity(node),
                    )
                )
        return functions

    def _complexity(self, node: ast.AST) -> int:
        """
        Cyclomatic complexity: start at 1 (one straight-line path through
        the code) and add one for every place execution can branch — an
        `if`, a loop, an `except` clause, an `and`/`or`, etc. The higher the
        number, the more test cases it takes to exercise every path.
        """
        complexity = 1
        for child in _own_body_nodes(node):
            if isinstance(child, (ast.If, ast.For, ast.AsyncFor, ast.While, ast.ExceptHandler, ast.Assert)):
                complexity += 1
            elif isinstance(child, ast.BoolOp):
                complexity += len(child.values) - 1
            elif isinstance(child, ast.comprehension):
                complexity += 1 + len(child.ifs)
        return complexity

    def _check_naming(self, tree: ast.AST) -> list[NamingViolation]:
        violations = []
        seen: set[tuple[str, str]] = set()

        def _flag(kind: str, name: str, lineno: int, reason: str) -> None:
            key = (kind, name)
            if key not in seen:
                seen.add(key)
                violations.append(NamingViolation(kind=kind, name=name, line_number=lineno, reason=reason))

        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                is_dunder = node.name.startswith("__") and node.name.endswith("__")
                if not is_dunder and not _SNAKE_CASE_RE.match(node.name):
                    _flag("function", node.name, node.lineno, "function names should be snake_case")
            elif isinstance(node, ast.ClassDef):
                if not _PASCAL_CASE_RE.match(node.name):
                    _flag("class", node.name, node.lineno, "class names should be PascalCase")
            elif isinstance(node, ast.Name) and isinstance(node.ctx, ast.Store):
                is_dunder = node.id.startswith("__") and node.id.endswith("__")
                if not is_dunder and not _SNAKE_CASE_RE.match(node.id) and not _CONSTANT_RE.match(node.id):
                    _flag("variable", node.id, node.lineno, "variable names should be snake_case or UPPER_CASE for constants")

        return violations

    def _find_unused_variables(self, tree: ast.AST) -> list[UnusedVariable]:
        results = []
        scopes: list[ast.AST] = [tree] + [
            node for node in ast.walk(tree) if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        ]

        for scope in scopes:
            assigned: dict[str, int] = {}
            for child in _own_body_nodes(scope):
                targets = self._assignment_targets(child)
                for target in targets:
                    for name_node in ast.walk(target):
                        if isinstance(name_node, ast.Name) and isinstance(name_node.ctx, ast.Store):
                            if not name_node.id.startswith("_"):
                                assigned[name_node.id] = name_node.lineno

            used: set[str] = set()
            for child in ast.walk(scope):
                if isinstance(child, ast.Name) and isinstance(child.ctx, ast.Load):
                    used.add(child.id)
                elif isinstance(child, ast.AugAssign) and isinstance(child.target, ast.Name):
                    used.add(child.target.id)

            scope_name = "module" if scope is tree else scope.name  # type: ignore[union-attr]
            for name, lineno in assigned.items():
                if name not in used:
                    results.append(UnusedVariable(name=name, line_number=lineno, scope=scope_name))

        return results

    @staticmethod
    def _assignment_targets(node: ast.AST) -> list[ast.AST]:
        if isinstance(node, ast.Assign):
            return list(node.targets)
        if isinstance(node, ast.AnnAssign) and node.target is not None:
            return [node.target]
        if isinstance(node, (ast.For, ast.AsyncFor)):
            return [node.target]
        if isinstance(node, ast.withitem) and node.optional_vars is not None:
            return [node.optional_vars]
        return []

    @staticmethod
    def _score(
        avg_complexity: float,
        naming_violation_count: int,
        unused_variable_count: int,
        long_function_count: int,
    ) -> float:
        score = 100.0
        if avg_complexity > 10:
            score -= min(30.0, (avg_complexity - 10) * 3)
        elif avg_complexity > 5:
            score -= (avg_complexity - 5) * 2
        score -= min(20.0, naming_violation_count * 2)
        score -= min(20.0, unused_variable_count * 4)
        score -= min(20.0, long_function_count * 5)
        return round(max(0.0, min(100.0, score)), 1)
