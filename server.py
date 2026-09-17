"""
Compatibility entry point.

The actual HTTP/webhook server is implemented in main.py.
Render should start the application with:

python main.py

This file is kept so old deployment commands do not immediately
break the project.
"""

from main import main


if __name__ == "__main__":
    main()
