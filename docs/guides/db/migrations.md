This guide explains how to manage database migrations in your project. Migrations are essential for evolving your database schema over time while preserving existing data.

## Creating a migration

To create a new migration after modifying your models, use the following command:

<!-- termynal -->
```bash
> kamihi db migrate
2025-01-01 at 00:00:00 | SUCCESS  | Migrated revision='xxxxxxxxxxxx'
```

This command will generate a new migration script in the `migrations/versions` directory. Review the generated script to ensure it accurately reflects the changes you made to your models.

## Applying migrations

Once you have created a migration, you need to apply it to your database. Use the following command to upgrade your database schema to the latest revision:

<!-- termynal -->
```bash
> kamihi db upgrade
2025-01-01 at 00:00:00 | SUCCESS  | Upgraded revision='xxxxxxxxxxxx'
```

This command will apply all pending migrations to your database.

## Downgrading migrations

If you need to revert to a previous migration, you can use the downgrade command. Specify the target revision you want to downgrade to:

<!-- termynal -->
```bash
> kamihi db downgrade <target_revision>
2025-01-01 at 00:00:00 | SUCCESS  | Downgraded revision='<target_revision>'
```

Replace `<target_revision>` with the specific revision identifier you want to revert to. You can also use relative revisions numbers (e.g., `-1` to go back one revision, `-5` to go back five revisions, etc.).
