# run.py

from api import create_app, db

# Create app instance here, not in __init__.py
app = create_app()

@app.shell_context_processor
def make_shell_context():
    return {
        "app": app,
        "db": db
    }

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0")
