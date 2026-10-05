# Code Impact Analyzer

A static-analysis tool for Python repositories that builds a dependency graph and identifies which parts of a codebase may be affected when a function, method, or class changes.

The project combines **Python AST analysis, dependency graphs, symbol resolution, and Git-based change detection** to provide developers with actionable impact information before modifying or reviewing code.

## Features

- **Python repository scanning**
  - Recursively discovers Python source files.
  - Builds a structured representation of the repository.

- **Symbol resolution**
  - Detects modules, classes, functions, and methods.
  - Resolves fully qualified symbols such as:
    ```text
    services.order.OrderService.create_order
    models.user.User.get_details
    ```

- **Dependency graph generation**
  - Tracks relationships between symbols.
  - Supports:
    - `imports`
    - `calls`

- **Method-call analysis**
  - Detects calls between methods and functions.
  - Builds caller → callee relationships.

- **Impact analysis**
  - Identifies symbols affected by a changed symbol.
  - Supports direct and indirect impact paths.

- **Risk classification**
  - Classifies affected symbols into:
    - HIGH
    - MEDIUM
    - LOW

- **Confidence scoring**
  - Assigns confidence based on dependency distance.
  - Direct dependencies receive higher confidence than deeper call-chain dependencies.

- **Git commit comparison**
  - Compares two Git commits.
  - Detects changed Python symbols between commits.
  - Example:
    ```text
    --from HEAD~1 --to HEAD
    ```

- **Change detection**
  - Uses Python AST representations to determine whether functions or methods changed.
  - Detects modifications to method bodies even when the surrounding file remains mostly unchanged.

- **Impact paths**
  - Shows the dependency chain leading from a changed symbol to affected symbols.

Example:

```text
models.user.User.get_details
        ↓
services.order.OrderService.create_order
        ↓
app.run_app
```

- **Repository validation**
  - Handles invalid repository paths.
  - Supports command-line symbol analysis.
  - Includes automated tests for core components.

---

## Architecture

```text
                    Python Repository
                           │
                           ▼
                  Repository Scanner
                           │
                           ▼
                    Symbol Resolver
                           │
              ┌────────────┴────────────┐
              ▼                         ▼
       Symbol Information        Import Information
              │                         │
              └────────────┬────────────┘
                           ▼
                    Graph Builder
                           │
                           ▼
                   Dependency Graph
                           │
              ┌────────────┴────────────┐
              ▼                         ▼
       Change Detector            Impact Analyzer
              │                         │
              ▼                         ▼
        Changed Symbols         Affected Symbols
                                        │
                                        ▼
                                Risk + Confidence
                                        │
                                        ▼
                                  CLI Report
```

---

## Project Structure

```text
Code Impact Analyser/
│
├── analyzer/
│   ├── analyze.py
│   ├── change_detector.py
│   ├── cli.py
│   ├── git_provider.py
│   ├── graph.py
│   ├── graph_builder.py
│   ├── impact.py
│   ├── resolver.py
│   └── scanner.py
│
├── examples/
│   └── sample_project/
│       ├── app.py
│       ├── models/
│       │   └── user.py
│       └── services/
│           ├── order.py
│           └── payment.py
│
├── tests/
│   ├── test_change_detector.py
│   ├── test_graph.py
│   ├── test_impact.py
│   ├── test_resolver.py
│   └── test_scanner.py
│
└── README.md
```

---

## Installation

Clone the repository and install the required dependencies.

```bash
git clone <repository-url>
cd Code-Impact-Analyser
```

Run the test suite:

```bash
python -m pytest
```

Current test suite:

```text
7 passed
```

---

## Usage

### Analyze a specific symbol

```bash
python -m analyzer.cli examples/sample_project --symbol models.user.User.get_details
```

Example output:

```text
Code Impact Analyzer
====================

Repository: examples\sample_project

Changed Symbol:
  models.user.User.get_details

Potentially affected:

  services.order.OrderService.create_order
    Relationship: calls
    Impact: direct
    Risk: HIGH
    Confidence: 100%

  app.run_app
    Relationship: calls
    Impact: indirect
    Risk: MEDIUM
    Confidence: 85%
```

The tool also displays the complete dependency path:

```text
models.user.User.get_details
        ↓
services.order.OrderService.create_order
        ↓
app.run_app
```

---

## Git-Based Change Analysis

The analyzer can compare two Git commits:

```bash
python -m analyzer.cli examples/sample_project --from HEAD~1 --to HEAD
```

Example:

```text
Comparing commits:
  From: HEAD~1
  To:   HEAD

Changed Symbols:
  services.order.OrderService.create_order
```

The analyzer then determines which symbols depend on the changed symbol.

Example:

```text
Impact of: services.order.OrderService.create_order

  app.run_app
    Relationship: calls
    Impact: direct
    Risk: HIGH
    Confidence: 100%
```

---

## Risk Analysis

The analyzer calculates an overall risk level based on the highest-risk affected symbol.

Example:

```text
Overall Risk
====================
Risk Level: HIGH
Changed Symbols: 1
Affected Symbols: 2
Affected Files: 2
HIGH Risk: 1
MEDIUM Risk: 1
LOW Risk: 0
```

### Risk interpretation

| Risk | Meaning |
|---|---|
| HIGH | Direct dependency or high-confidence impact |
| MEDIUM | Indirect dependency through a call chain |
| LOW | More distant or lower-confidence dependency |

---

## Confidence Scoring

Confidence decreases as the dependency distance increases.

| Dependency Distance | Confidence |
|---:|---:|
| 1 | 100% |
| 2 | 85% |
| 3 | 70% |
| 4+ | 60% |

For example:

```text
Changed Symbol
      ↓
Direct Caller       → 100%
      ↓
Indirect Caller     → 85%
```

This provides developers with an indication of how strongly an affected symbol is connected to the original change.

---

## Dependency Graph

The graph builder can display relationships discovered in the repository.

Example:

```text
examples\sample_project\app.py
  --[imports]--> models.user.User
  --[imports]--> services.order.OrderService

examples\sample_project\services\order.py
  --[imports]--> models.user.User
  --[imports]--> services.payment.PaymentService

app.run_app
  --[calls]--> services.order.OrderService.create_order

services.order.OrderService.create_order
  --[calls]--> models.user.User.get_details
```

This graph forms the basis for the impact-analysis stage.

---

## Change Detection

The change detector parses both versions of a Python file using the `ast` module.

Instead of relying only on line-based differences, it extracts individual symbols and compares their AST representations.

For example:

```python
def create_order(self, user):
    return "completed"
```

changing to:

```python
def create_order(self, user):
    return "complete"
```

is detected as a change to:

```text
services.order.OrderService.create_order
```

This allows the analyzer to report **which symbol changed**, rather than simply reporting that a file changed.

---

## Quantitative Results

The current implementation has been validated with automated tests and a sample repository.

### Current project metrics

```text
Test cases:             7
Tests passing:          7
Tests failing:          0

Dependency relations:
  Imports
  Method calls

Impact levels:
  Direct
  Indirect

Risk levels:
  HIGH
  MEDIUM
  LOW

Git comparison:
  Supported

Symbol-level change detection:
  Supported
```

### Sample impact analysis

For the sample project, changing:

```text
models.user.User.get_details
```

identified:

```text
2 affected symbols
2 affected files
1 HIGH-risk direct dependency
1 MEDIUM-risk indirect dependency
```

The detected call chain was:

```text
User.get_details
      ↓
OrderService.create_order
      ↓
app.run_app
```

---

## Testing

Run the complete test suite:

```bash
python -m pytest
```

Current result:

```text
============================== 7 passed ==============================
```

The tests cover:

- Change detection
- Dependency graph construction
- Impact analysis
- Symbol resolution
- Repository scanning

---

## Example Workflow

A typical workflow is:

### 1. Scan the repository

```text
Repository
    ↓
Python files
```

### 2. Resolve symbols

```text
Files
    ↓
Modules
    ↓
Classes
    ↓
Methods / Functions
```

### 3. Build dependencies

```text
Symbols
    ↓
Imports + Calls
    ↓
Dependency Graph
```

### 4. Detect Git changes

```text
HEAD~1
   ↓
AST comparison
   ↓
Changed symbols
```

### 5. Calculate impact

```text
Changed Symbol
      ↓
Dependency Graph
      ↓
Direct / Indirect Dependencies
```

### 6. Generate risk report

```text
Affected Symbols
      ↓
Risk
      ↓
Confidence
      ↓
Impact Paths
```

---

## Technologies Used

- **Python**
- **Python AST**
- **Git**
- **Pytest**
- **Graph-based dependency analysis**
- **Static code analysis**

---

## Key Engineering Concepts Demonstrated

This project demonstrates practical implementation of:

- Static analysis
- Abstract Syntax Trees
- Symbol resolution
- Dependency graphs
- Call graph construction
- Git-based source comparison
- Change impact analysis
- Risk classification
- Confidence scoring
- CLI application design
- Automated testing

---

## Future Improvements

Potential extensions include:

- Cross-module variable tracking
- More accurate dynamic dispatch resolution
- Decorator analysis
- Inheritance-based dependency tracking
- API endpoint impact detection
- Test-to-code dependency mapping
- JSON output for CI/CD pipelines
- HTML impact reports
- GitHub Actions integration
- Pull-request impact analysis
- Visualization of dependency graphs
- Support for larger Python repositories
- Incremental graph updates
- Performance benchmarking on large repositories

---

## Resume Highlights

Possible resume bullets based on the implemented functionality:

- **Built a Python static-analysis tool that constructs symbol-level dependency graphs and detects direct/indirect code impact using AST parsing and Git commit comparison.**
- **Implemented Git-based symbol change detection and call-graph analysis, identifying affected symbols, dependency paths, risk levels, and confidence scores.**
- **Developed a dependency analysis pipeline covering repository scanning, symbol resolution, graph construction, change detection, and impact analysis, validated with 7 automated tests.**
- **Implemented multi-level impact analysis that traced dependency chains and quantified affected symbols/files with HIGH, MEDIUM, and LOW risk classification.**

> Only use metrics such as **7 tests, 2 affected symbols, 2 affected files, 100%/85% confidence**, etc. when they are actually produced by your implementation or test/demo repository. For resume claims about performance or large-scale repositories, benchmark them first rather than estimating.

---

## Author

**Yashwanth K.**

