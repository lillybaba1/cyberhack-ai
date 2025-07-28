import sympy as sp  # Mock risk scoring; replace with ML models

def calculate_risk(vulns: int) -> float:
    x = sp.symbols('x')
    eq = sp.Eq(x**2 - vulns, 0)
    solution = sp.solve(eq, x)
    return float(solution[0]) if solution else 0.0

# Example: print(calculate_risk(10)) -> ~3.16 (sqrt risk)
