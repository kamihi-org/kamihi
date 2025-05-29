This guide details the documentation standards and contribution process for the Kamihi project, establishing clear guidelines to ensure consistency, clarity, and maintainability across all project documentation.

## Intended audiences

Documentation in this project serves multiple audiences: new users learning to use the tools, knowledgeable developers implementing features and new contributors seeking to understand the codebase. The documentation you write should take into account your intended audience.

## Style guide

### Writing Principles

**Clarity and Conciseness**: Write for your future self and new contributors. Every sentence should serve a purpose. Remove unnecessary words and avoid redundant explanations.

**Active Voice**: Use active voice consistently. Write "Run the command" instead of "The command should be run."

**Present Tense**: Document current functionality in present tense. Write "The function returns" instead of "The function will return."

### Language Standards

**Technical Terminology**: Use precise technical terms consistently. When introducing new concepts, provide brief explanations or link to definitions.

**Code References**: Use backticks for inline code, function names, file paths, and configuration values. Example: `uv run mkdocs serve` or `setup.md`.

**Commands and Examples**: Provide complete, runnable examples. Include expected output when helpful for verification.

### Formatting Conventions

**Headers**: Use sentence case for headers. Follow the established hierarchy:
- `##` for main sections
- `###` for subsections  
- `####` for detailed topics

!!! note
    The first-level header (`#`) is filled by the documentation framework from the title in `mkdocs.yml`. Use `##` for the first-level sections of your document.

**Lists**: Use bullet points for unordered information, numbered lists for sequential steps. Keep list items parallel in structure.

**Code Blocks**: Specify language for syntax highlighting. Include the command prompt or expected environment when relevant:

```bash
> uv run mkdocs serve
```

**File Paths**: Use relative paths when possible. Always include the filepath comment for documentation files.

### Content Organization

**One Concept Per Section**: Each section should focus on a single main idea that can be summarized in one sentence.

**Logical Flow**: Structure content to build understanding progressively. Start with concepts, then provide implementation details.

**Cross-References**: Link related sections and external resources. Use descriptive link text rather than "click here." Always use relative links to maintain portability across environments.

## Organization

This project uses MkDocs with Material theme for documentation generation. The documentation follows a "docs-as-code" approach, versioned alongside the codebase.

**File Structure**:
- `/docs/` - All documentation source files
- `/docs/tutorials/` - Step-by-step learning guides for new users
- `/docs/guides/` - Task-oriented how-to documentation organized by topic
- `/docs/reference/` - Technical reference material (CLI, API)
- `/docs/explanation/` - Conceptual documentation and background theory
- `/docs/dev/` - Developer-focused documentation for contributors
- `/docs/images/` - Documentation assets and media files
- `/docs/stylesheets/` - Custom CSS for documentation styling
- `mkdocs.yml` - Site configuration and navigation structure

### Contribution Workflow

**Documentation Changes**: Include documentation updates in the same pull request as related code changes. This ensures synchronization and provides context for reviewers.

**Review Process**: Documentation changes undergo the same review process as code. Reviewers should verify accuracy, clarity, and adherence to style guidelines.

**Testing**: Always test documentation locally before submitting. Verify that code examples work and links resolve correctly.

## Documentation live

You can view the documentation on a local server with live reload. For that, and assuming you have the project set up following the [setup guide](setup.md), run:

```bash
uv run mkdocs serve
```

This will start a local server at `http://localhost:8000`, where you can see the documentation. The server will automatically reload when you make changes to the documentation files.
