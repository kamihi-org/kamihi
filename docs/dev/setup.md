This guide will help you set up the development environment for the project.

## Prerequisites

You should have the following installed:

- `git`, for version control. You can find download and installation instructions [here](https://git-scm.com/downloads).
- `uv`, for managing virtual environments and dependencies. Install it using [this guide](https://docs.astral.sh/uv/getting-started/installation/).
- (optional) `docker` and `docker compose`, for running the database and functional tests. You can install Docker Desktop from [here](https://docs.docker.com/desktop/) or follow the instructions for [Docker Engine](https://docs.docker.com/engine/install/) and [Docker Compose](https://docs.docker.com/compose/install/).
- (if not using Docker) `mongodb`, for running the database locally. You can find installation instructions [here](https://www.mongodb.com/docs/manual/installation/).

## Setting up the project

1. Clone the repository:
    ```bash
    git clone https://github.com/kamihi-dev/kamihi.git
    cd kamihi
    ```
2. Create the virtual environment and install dependencies:
    ```bash
    uv sync --all-packages --all-groups
    ```
3. Activate the virtual environment by restarting your terminal or sourcing the `activate` file for your terminal type:
    ```bash
    # For bash/zsh
    source .venv/bin/activate

    # For fish
    source .venv/bin/activate.fish

    # For csh/tcsh
    source .venv/bin/activate.csh

    # For powershell
    . .venv/Scripts/Activate.ps1
    ```
4. (optional) We recommend also setting up a test project to experiment with the framework and the code you write. Just create a new project using the CLI, and substitute the `pyproject.toml` file with this one:
    ```toml
    [project]
    name = "kamihi-example"
    version = "0.0.0"
    description = "Kamihi project"
    readme = "README.md"
    requires-python = ">=3.12"
    dependencies = [
        "kamihi",
    ]

    [tool.uv.sources]
    kamihi = { path = "<the path to the kamihi project>", editable = true }
    ```

For more information specific to documentation and testing, refer to the [documentation guide](documentation.md) and the [testing guide](testing.md).
