from cape_webservices import webapp_core
from logging import debug, info


if __name__ == '__main__':
    import sys

    port = int(sys.argv[1]) if len(sys.argv) == 2 else None

    if port is not None and port <= 0:
        info("Pre-initialized and pre-compiled all dependencies")
        sys.exit(0)

    debug(f"Initializing on port {port}")
    webapp_core.run(port=port)
