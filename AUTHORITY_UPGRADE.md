# Protocol: Level 5 Authority Upgrade (Database Control)

To grant the Omni-System full capability to create/destroy tables and manage the database architecture autonomously:

## 1. Retrieve Connection String

1. Log in to **Supabase Dashboard**.
2. Go to **Project Settings** (Gear Icon).
3. Select **Database**.
4. Scroll to **Connection String**.
5. Click **URI**.
6. Copy the string. It looks like:
    `postgresql://postgres.rzcpfwkygdvoshtwxncs:[YOUR-PASSWORD]@aws-0-us-east-1.pooler.supabase.com:6543/postgres`

## 2. Update Environment

1. Open your `.env` file in VS Code.
2. Add a new line at the bottom:

    ```bash
    DATABASE_URL=postgresql://postgres.rzcpfwkygdvoshtwxncs:[YOUR-PASSWORD]...
    ```

    *(Replace `[YOUR-PASSWORD]` with your actual database password)*

3. Save the file.

## 3. Activation

Once added, the system can use `psycopg2` to execute raw SQL (DDL) commands, enabling:

- Self-healing database schemas.
- Automatic creation of new agent memories.
- Zero-touch migrations.
