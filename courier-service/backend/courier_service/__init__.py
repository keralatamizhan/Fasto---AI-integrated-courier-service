
"""
Courier Service Django project package.

We prefer `mysqlclient`, but on Windows it's common to use PyMySQL during early setup.
If `MySQLdb` is unavailable, install PyMySQL and this will allow Django's MySQL backend
to work without code changes.
"""

try:
    import MySQLdb  # type: ignore  # noqa: F401
except Exception:
    try:
        import pymysql

        pymysql.install_as_MySQLdb()
    except Exception:
        # No MySQL driver installed; SQLite fallback can still run.
        pass

