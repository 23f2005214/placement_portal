import sqlite3


def column_exists(cur, table: str, column: str) -> bool:
    cur.execute(f"PRAGMA table_info({table})")
    return any(row[1] == column for row in cur.fetchall())


def main():
    conn = sqlite3.connect("placement_portal.db")
    try:
        cur = conn.cursor()

        table = "company_profiles"
        col = "is_approved"

        if not column_exists(cur, table, col):
            cur.execute(f"ALTER TABLE {table} ADD COLUMN {col} BOOLEAN NOT NULL DEFAULT 0")

        # Backfill from approval_status for existing rows
        cur.execute(
            f"""
            UPDATE {table}
            SET {col} = CASE
                WHEN approval_status = 'approved' THEN 1
                ELSE 0
            END
            """
        )

        conn.commit()

        cur.execute(f"SELECT COUNT(1) FROM {table} WHERE {col} = 1")
        approved = cur.fetchone()[0]
        cur.execute(f"SELECT COUNT(1) FROM {table}")
        total = cur.fetchone()[0]
        print(f"Migration complete. {approved}/{total} companies approved.")
    finally:
        conn.close()


if __name__ == "__main__":
    main()

