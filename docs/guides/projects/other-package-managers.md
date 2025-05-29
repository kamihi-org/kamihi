This guide explains how to install and set up Kamihi projects using package managers other than `uv`. While Kamihi's templates and documentation default to `uv`, you can successfully use `pip` with virtual environments or `Poetry` for dependency management.

## Prerequisites

- Python 3.12 or higher installed on your system
- Basic familiarity with Python package management
- For Poetry: Poetry installed on your system ([installation guide](https://python-poetry.org/docs/#installation))

## Why use alternative package managers

While `uv` offers exceptional performance and modern features, you might prefer other package managers for various reasons:

- **Team consistency**: Your team already uses `pip` or Poetry
- **Tooling integration**: Existing CI/CD pipelines or IDE configurations
- **Familiarity**: Comfort with established workflows
- **Corporate policies**: Organization requirements for specific tools

## Installation approaches

### Using pip with virtual environments

This approach uses Python's built-in `venv` module with `pip` for dependency management.

#### Creating a new project

1. **Create and navigate to your project directory:**

    ```bash
    mkdir hello-world
    cd hello-world
    ```

2. **Create a virtual environment:**

    ```bash
    python -m venv .venv
    ```

3. **Activate the virtual environment:**

    === "Linux/macOS"

        ```bash
        source .venv/bin/activate
        ```

    === "Windows (Command Prompt)"

        ```cmd
        .venv\Scripts\activate.bat
        ```

    === "Windows (PowerShell)"

        ```powershell
        .venv\Scripts\Activate.ps1
        ```

4. **Install Kamihi:**

    ```bash
    pip install kamihi
    ```

5. **Create project structure manually:**

    Since `kamihi init` creates a `uv`-based project, you'll need to adapt the structure:

    ```bash
    # Create necessary directories
    mkdir actions models
    mkdir actions/start
    
    # Create __init__.py files
    touch actions/__init__.py
    touch actions/start/__init__.py
    touch models/__init__.py
    ```

6. **Create essential files:**

    Create a `requirements.txt` file for dependency management:

    ```txt
    kamihi>=1.0.0
    ```

    Create a basic `kamihi.yml` configuration file:

    ```yaml
    ---
    token: YOUR_TOKEN_HERE
    timezone: UTC
    ```

    Create a sample action in `actions/start/start.py`:

    ```python
    from kamihi import bot
    from telegram import Update
    from telegram.ext import ContextTypes

    @bot.action(description="Start the bot")
    async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle the /start command."""
        await update.message.reply_text("Hello! I'm your Kamihi bot.")
    ```

#### Running your project

1. **Ensure your virtual environment is activated:**

    The command prompt should show `(.venv)` prefix when activated.

2. **Run the bot:**

    ```bash
    kamihi run
    ```

#### Managing dependencies

To add new dependencies to your project:

```bash
# Install a new package
pip install package-name

# Update requirements.txt
pip freeze > requirements.txt
```

To install dependencies on a new machine:

```bash
# Activate virtual environment first
source .venv/bin/activate  # Linux/macOS
# or
.venv\Scripts\activate.bat  # Windows

# Install dependencies
pip install -r requirements.txt
```

### Using Poetry

Poetry provides a more modern approach to Python dependency management with automatic virtual environment handling.

#### Creating a new project

1. **Initialize a new Poetry project:**

    ```bash
    poetry new hello-world
    cd hello-world
    ```

2. **Add Kamihi as a dependency:**

    ```bash
    poetry add kamihi
    ```

3. **Create project structure:**

    Poetry creates a different directory structure by default. Adapt it for Kamihi:

    ```bash
    # Remove the default package directory if it exists
    rm -rf hello_world/

    # Create Kamihi-expected directories
    mkdir actions models
    mkdir actions/start
    
    # Create __init__.py files
    touch actions/__init__.py
    touch actions/start/__init__.py
    touch models/__init__.py
    ```

4. **Create essential files:**

    Create a `kamihi.yml` configuration file:

    ```yaml
    ---
    token: YOUR_TOKEN_HERE
    timezone: UTC
    ```

    Create a sample action in `actions/start/start.py`:

    ```python
    from kamihi import bot
    from telegram import Update
    from telegram.ext import ContextTypes

    @bot.action(description="Start the bot")
    async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle the /start command."""
        await update.message.reply_text("Hello! I'm your Kamihi bot.")
    ```

#### Running your project

1. **Run the bot using Poetry:**

    ```bash
    poetry run kamihi run
    ```

    Alternatively, you can activate Poetry's virtual environment:

    ```bash
    poetry shell
    kamihi run
    ```

#### Managing dependencies

Poetry simplifies dependency management:

```bash
# Add a new dependency
poetry add package-name

# Add a development dependency
poetry add --group dev package-name

# Update dependencies
poetry update

# Install dependencies (useful for new machines)
poetry install
```

## Converting existing uv projects

If you have an existing Kamihi project created with `uv` that you want to convert:

### Converting to pip + venv

1. **Create and activate a virtual environment:**

    ```bash
    python -m venv .venv
    source .venv/bin/activate  # Linux/macOS
    # or
    .venv\Scripts\activate.bat  # Windows
    ```

2. **Convert dependencies:**

    Extract dependencies from `pyproject.toml` and create `requirements.txt`:

    ```bash
    # If uv is still available
    uv pip compile pyproject.toml -o requirements.txt
    
    # Or manually create requirements.txt based on pyproject.toml dependencies
    ```

3. **Install dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

4. **Remove uv-specific files (optional):**

    ```bash
    rm uv.lock  # If you no longer need uv
    ```

### Converting to Poetry

1. **Initialize Poetry in the existing directory:**

    ```bash
    poetry init
    ```

2. **Add dependencies from pyproject.toml:**

    Poetry can read the existing `pyproject.toml` if it follows standard format:

    ```bash
    poetry install
    ```

    Or manually add each dependency:

    ```bash
    poetry add kamihi
    # Add other dependencies as needed
    ```

3. **Remove uv-specific files (optional):**

    ```bash
    rm uv.lock  # If you no longer need uv
    ```

## Important considerations

### Virtual environment activation

Unlike `uv`, which can automatically manage Python environments, `pip` requires manual virtual environment activation. Always ensure your virtual environment is activated before running commands.

### Dependency resolution

- **uv**: Provides fast, deterministic dependency resolution
- **pip**: May require manual conflict resolution for complex dependencies
- **Poetry**: Provides deterministic resolution similar to uv but may be slower

### Performance differences

`uv` typically offers significantly faster installation and resolution times compared to `pip` and Poetry. If performance is critical, consider using `uv` even if your team prefers other tools for some workflows.

### Docker deployment

When deploying with Docker, you may need to adapt the Dockerfile provided by Kamihi templates. The default Dockerfile uses `uv` for multi-stage builds and optimized performance.

## Notes

- Kamihi's core functionality remains the same regardless of the package manager used
- The `kamihi` CLI commands work identically across all package managers
- Consider your team's existing toolchain and workflows when choosing a package manager
- All package managers can coexist in the same environment if needed for different projects
