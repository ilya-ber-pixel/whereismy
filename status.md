запустили
 alembic revision --autogenerate -m "Initial database schema"
 получили
 context.run_migrations()
/workspace/venv/bin/alembic:10: SAWarning: Can't validate argument 'native_enum'; can't locate any SQLAlchemy dialect named 'native'
  sys.exit(main())
  Generating /workspace/alembic/versions/532cce7a747e_initial_database_schema.py ...  done
((venv) ) vscode ➜ /workspace $ ^C
