from setuptools import setup

extras_require = {}
extras_require["lint"] = sorted(set(["pyflakes", "black"]))
extras_require["test"] = sorted(
    set(
        [
            "check-manifest",
            "pytest~=6.0",
            "pytest-cov~=2.8",
            "pytest-console-scripts~=0.2",
            "pytest-mock~=3.0",
        ]
    )
)
extras_require["develop"] = sorted(
    set(
        extras_require["test"]
        + extras_require["lint"]
        + ["check-manifest", "bumpversion~=0.5", "pre-commit", "twine", "jupyter"]
    )
)
extras_require["complete"] = sorted(set(sum(list(extras_require.values()), [])))

setup(
    extras_require=extras_require,
    use_scm_version=lambda: {"local_scheme": lambda version: ""},
)
