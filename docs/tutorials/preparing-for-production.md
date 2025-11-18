In this final tutorial, you will prepare your movie rentals bot for production use. You will harden configuration, improve logging, review permissions, and think through practical deployment considerations.

By the end of this tutorial, you will have a checklist and concrete configuration changes that make your bot safer, more observable, and ready to be deployed.

## Prerequisites

- You have followed the earlier tutorials and have a fully functional movie rentals bot using Sakila.
- You are familiar with your host environment (local server, container platform, or other).

## Separating development and production configuration

- Differentiate dev vs prod environments.
- Use environment variables to override sensitive values in `kamihi.yaml`.
- Configure DB connections, Sakila datasource, and tokens via env vars.

## Securing secrets and sensitive data

- Keep `kamihi.yaml` out of version control when it contains secrets.
- Store tokens and passwords in environment variables or secret managers.
- Regenerate and rotate tokens as needed.

## Production-grade database and Sakila connectivity

- Move the Kamihi DB from ephemeral SQLite to a production database if appropriate.
- Confirm migrations are applied on startup or via a deployment step.
- Ensure the Sakila datasource is reachable and configured read-only.

## Logging, rotation, and notifications

- Configure log level, rotation, and retention in Kamihi settings.
- Consider structured logging for better searchability.
- Add notification channels for critical errors, if available.

## Reviewing roles, permissions, and admin access

- Audit which roles exist and what actions they can use.
- Ensure only trusted users are admins and managers.
- Protect the admin web interface with network and authentication safeguards.

## Testing and smoke checks before deployment

- Define a small set of smoke tests:
  - `/start` responds.
  - Sakila queries work.
  - Favorite store selection and locations work.
  - Renting and returning a film works.
  - Jobs run manually from the admin web interface.
- Incorporate these checks into your deployment routine.

## Deployment patterns and operational concerns

- Outline common deployment patterns:
  - Systemd service.
  - Docker container.
- Discuss:
  - Setting environment variables.
  - Mounting `static/` media.
  - Handling timezones and job schedules.
  - Monitoring and automated restarts.

## TL;DR

- Move secrets and environment-specific settings out of source control.
- Use environment variables to configure Kamihi and Sakila for production.
- Switch to a production-ready database for Kamihi data where appropriate.
- Configure logging and review roles and permissions.
- Establish a small set of smoke tests and choose a deployment pattern that fits your infrastructure.

## What's next?

With your movie rentals bot running in production, you can iterate on new features, integrate external services, or adapt the same patterns to other domains. Refer back to the guides and reference documentation as you expand your bot's capabilities.