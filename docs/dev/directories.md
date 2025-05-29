This page details the organizational strategy for the repository, and all its files


## Project Structure Overview

The Kamihi repository follows standard Python project conventions:

```
kamihi/
├── src/kamihi/                 # Source code
├── tests/                      # Test suites
├── docs/                       # Documentation source
├── README.md                   # Project overview and quick start
├── LICENSE.md                  # MIT license
├── CHANGELOG.md                # Version history
├── pyproject.toml              # Project configuration and dependencies
├── uv.lock                     # Dependency lock file
├── mkdocs.yml                  # Documentation configuration
├── .env.sample                 # Sample environment variable file
├── .python-version             # Python version specification
├── .deepsource.toml            # DeepSource configuration for static analysis
├── .pre-commit-config.yaml     # Pre-commit hooks configuration
├── .gitignore                  # Git ignore rules
└── .dockerignore               # Docker ignore rules
```

## Source Code Organization (`src/kamihi/`)

```
src/kamihi/
├── __init__.py                 # Public API exports and bot instance
├── py.typed                    # Type checking marker
├── base/                       # Core framework utilities
├── bot/                        # Bot orchestration and action registry
├── cli/                        # Command-line interface
├── db/                         # Database abstraction layer
├── templates/                  # Templating system
├── tg/                         # Telegram client integration
├── users/                      # User management and permissions
└── web/                        # Admin web interface
```

### Base module (`src/kamihi/base/`)

Core framework utilities that other modules depend on:

```
base/
├── __init__.py                 # Module exports
├── config.py                   # Pydantic configuration schemas
├── logging.py                  # Centralized logging configuration
└── manual_send.py              # Utility for sending Telegram messages manually
```

### CLI module (`src/kamihi/cli/`)

Command-line interface for project management and development:

```
cli/
├── __init__.py                 # Module exports
├── cli.py                      # Main CLI application and context
├── commands/                   # Individual command implementations
│   ├── __init__.py
│   ├── init.py                 # Project initialization
│   ├── run.py                  # Bot execution
│   ├── action.py               # Action scaffolding
│   ├── user.py                 # User management
│   └── version.py              # Version information
└── templates/                  # CLI scaffolding templates
```

### Bot module (`src/kamihi/bot/`)

Core bot orchestration and action management system:

```
bot/
├── __init__.py                 # Module exports
├── action.py                   # Action registration and execution logic
├── bot.py                      # Main bot class and orchestration
├── utils.py                    # Bot utility functions
└── models/                     # Bot-related data models
    ├── __init__.py
    └── registered_action.py    # Action registry data model
```

### Database module (`src/kamihi/db/`)

Database abstraction layer for persistent storage:

```
db/
├── __init__.py                 # Module exports
└── mongo.py                    # MongoDB integration and utilities
```

### Templates module (`src/kamihi/templates/`)

Templating system for dynamic content generation:

```
templates/
├── __init__.py                 # Module exports
└── templates.py                # Template processing and rendering
```

### Telegram module (`src/kamihi/tg/`)

Telegram client integration and message handling:

```
tg/
├── __init__.py                 # Module exports
├── client.py                   # Telegram client configuration
├── default_handlers.py         # Standard message handlers
├── send.py                     # Message sending utilities
└── handlers/                   # Specialized message handlers
    ├── __init__.py
    └── auth_handler.py          # Authentication handling
```

### Users module (`src/kamihi/users/`)

User management and permission system:

```
users/
├── __init__.py                 # Module exports
├── users.py                    # User management logic
└── models/                     # User-related data models
    ├── __init__.py
    ├── permission.py           # Permission model
    ├── role.py                 # Role-based access control
    └── user.py                 # User data model
```

### Web module (`src/kamihi/web/`)

Admin web interface for bot management:

```
web/
├── __init__.py                 # Module exports
├── views.py                    # Web view controllers
├── web.py                      # Web application configuration
├── static/                     # Static web assets
│   └── images/                 # Image resources
└── templates/                  # HTML templates
    └── home.html               # Main dashboard template
```

## Documentation structure (`docs/`)

Documentation follows the Diátaxis framework for comprehensive coverage:

```
docs/
├── index.md                    # Landing page and overview
├── changelog.md                # User-facing version history
├── thanks.md                   # Acknowledgments
├── tutorials/                  # Learning-oriented guides
├── guides/                     # Task-oriented how-to documentation
├── reference/                  # Technical reference material
├── dev/                        # Documentation for developers and contributors of the project
├── images/                     # Documentation assets
└── stylesheets/                # Custom documentation styling
```

## Test structure (`tests/`)

Testing structure mirrors source code organization while supporting multiple testing strategies:

```
tests/
├── __init__.py                 # Test package initialization
├── unit/                       # Fast, isolated unit tests
└── functional/                 # Integration tests with Docker
```
