# Windows 11 PostgreSQL Setup Guide

This guide connects a Windows 11 development machine to the existing **Phase 2** database layer. It creates the local `career_copilot` PostgreSQL database, configures the private `.env` file, applies Alembic migration `20260820_0001`, and verifies the seven tables. It does **not** add resume upload, parsing, matching, AI, or any Phase 3 functionality.

> Keep passwords and connection URLs private. The values below are placeholders only; do not commit a real `.env` file to Git.

## 1. Install PostgreSQL on Windows 11

Download the Windows installer certified by EDB from the official PostgreSQL Windows download page. The installer includes PostgreSQL Server, pgAdmin, and Stack Builder; select **PostgreSQL Server** and **Command Line Tools** during installation. pgAdmin is optional but useful for visually inspecting the local database. [1] [2]

Run the installer as an administrator. Choose a PostgreSQL superuser password for the local `postgres` account, keep the default port **5432** unless it conflicts with another service, and complete the wizard. The installer normally places command-line tools under a directory such as `C:\Program Files\PostgreSQL\16\bin`; add that `bin` directory to the Windows `Path` environment variable if `psql` is not recognized in a new PowerShell window. [2]

Open a **new** PowerShell window and confirm the client is available:

```powershell
psql --version
```

If the command returns a PostgreSQL version, the client tools are ready.

## 2. Create the database user and database

Connect as the local PostgreSQL superuser. PowerShell will prompt for the password that you chose during installation; do not type that password into a script or commit it anywhere.

```powershell
psql -U postgres -d postgres -W
```

At the `postgres=#` prompt, run the following SQL. Replace the password placeholder only in your local terminal with a strong local development password.

```sql
CREATE ROLE career_copilot
  WITH LOGIN PASSWORD '<choose-a-strong-local-password>';

CREATE DATABASE career_copilot
  OWNER career_copilot;

\q
```

To confirm that the role can connect, run:

```powershell
psql -U career_copilot -d career_copilot -h localhost -W
```

Then type `\q` to exit after the connection succeeds.

## 3. Configure `DATABASE_URL` in the private `.env` file

From the project root, open the backend directory. Copy the non-secret template named `env.example` to a local `.env` file; the `.env` file is ignored by Git.

```powershell
cd backend
Copy-Item env.example .env
notepad .env
```

Set `DATABASE_URL` in `backend\.env` to this form, replacing the password placeholder locally:

```text
DATABASE_URL=postgresql+psycopg://career_copilot:<url-encoded-local-password>@localhost:5432/career_copilot
```

The project accepts only `postgresql://` or `postgresql+psycopg://` schemes for database-backed work. If the password contains reserved URL characters such as `@`, `:`, `/`, `?`, or `#`, percent-encode those characters before placing it in the URL. Do not place an actual URL in source code, documentation, or a public issue.

## 4. Install backend dependencies and apply the migration

Use a project-local Python virtual environment. In PowerShell, run:

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m alembic upgrade head
```

The final command applies Alembic revision `20260820_0001`, which creates the Phase 2 schema. To see the current applied revision afterward, run:

```powershell
python -m alembic current
```

## 5. Verify all seven tables

From the activated `backend` virtual environment, verify the revision and table set. The following PowerShell command uses the private environment variable only at execution time:

```powershell
psql $env:DATABASE_URL -c "SELECT version_num FROM alembic_version;"

psql $env:DATABASE_URL -c "SELECT tablename FROM pg_tables WHERE schemaname = 'public' AND tablename IN ('users', 'resumes', 'jobs', 'skills', 'resume_skills', 'job_skills', 'match_results') ORDER BY tablename;"
```

The query must return exactly these seven tables:

| Table | Phase 2 responsibility |
| --- | --- |
| `users` | Candidate profile ownership. |
| `resumes` | Resume metadata and future storage reference. |
| `jobs` | Stored job-description records. |
| `skills` | Canonical reusable skills. |
| `resume_skills` | Resume-to-skill evidence. |
| `job_skills` | Job-to-skill requirements. |
| `match_results` | Reserved future analysis persistence contract. |

You can also use the interactive PostgreSQL terminal and the `\dt` meta-command to list tables. `psql` supports direct connection strings and interactive query execution. [3]

## 6. Common connection and migration errors

| Symptom | Likely cause | Safe resolution |
| --- | --- | --- |
| `psql` is not recognized | PostgreSQL `bin` directory is not on `Path`. | Add `C:\Program Files\PostgreSQL\<version>\bin` to the Windows `Path`, then open a new PowerShell window. |
| `connection refused` or `could not connect to server` | PostgreSQL service is stopped, port is wrong, or another service occupies the port. | Open `services.msc`, start the PostgreSQL service, and confirm `localhost:5432` matches your install choice. |
| `password authentication failed` | Wrong password, user, or a URL-special character was not encoded. | Re-enter the local password, confirm the user is `career_copilot`, and percent-encode reserved URL characters. |
| `database "career_copilot" does not exist` | Database creation step was skipped or targeted at another server. | Connect as `postgres` and rerun the `CREATE DATABASE career_copilot OWNER career_copilot;` statement. |
| `DATABASE_URL must use a PostgreSQL connection scheme` | The environment value is missing or points to a non-PostgreSQL service. | Correct the private `.env` file to use `postgresql+psycopg://...`; do not alter application code. |
| `No module named alembic` or `No module named psycopg` | The virtual environment is inactive or dependencies are missing. | Activate `.venv` and rerun `python -m pip install -r requirements.txt`. |
| `relation ... does not exist` | Migration has not been applied to this database. | From `backend`, run `python -m alembic upgrade head`, then verify with `python -m alembic current`. |
| `permission denied` during migration | The configured role does not own the database or lacks schema rights. | Recreate the database with `career_copilot` as owner, or have a local administrator grant the necessary privileges. |

## 7. Final local verification

Run the backend tests after the migration succeeds:

```powershell
cd backend
.\.venv\Scripts\Activate.ps1
python -m pytest
```

The tests verify configuration safeguards and core model relationships. They do not replace the PostgreSQL table check above, which confirms the migration was applied to your local server.

## References

[1] [PostgreSQL Windows installers](https://www.postgresql.org/download/windows/)

[2] [EDB: Installing PostgreSQL on Windows](https://www.enterprisedb.com/docs/supported-open-source/postgresql/installing/windows/)

[3] [PostgreSQL `psql` documentation](https://www.postgresql.org/docs/current/app-psql.html)
