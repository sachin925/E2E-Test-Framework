[tool.ruff]
line-length = 100
target-version = "py311"

[tool.ruff.lint]
select = [
    "E",   # pycodestyle errors
    "W",   # pycodestyle warnings
    "F",   # pyflakes
    "I",   # isort
    "B",   # flake8-bugbear
    "C4",  # flake8-comprehensions
    "UP",  # pyupgrade
]
ignore = [
    "E501",  # line too long (handled by formatter)
    "B008",  # do not perform function calls in argument defaults
]

[tool.ruff.lint.isort]
known-first-party = ["libraries"]

[tool.robocop]
exclude = ["too-many-calls-in-keyword", "too-long-keyword"]
configure = [
    "line-too-long:line_length:120"
]

[tool.robotidy]
line-length = 120
separator = "space"
spacecount = 4
