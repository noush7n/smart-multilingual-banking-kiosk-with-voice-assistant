"""Start the kiosk app:  python run.py"""
from backend import create_app

app = create_app()

if __name__ == "__main__":
    # 127.0.0.1 = this computer only. debug=True auto-reloads on code changes.
    app.run(host="127.0.0.1", port=5000, debug=True)