"""Root python script for MoU Dashboard web application."""

import argparse
import logging

import coloredlogs  # type: ignore[import]

# local imports
from web_app.config import app, get_config_vars, log_config_vars

from . import layout


def main(debug: bool) -> None:
    """Start up application context."""
    # Set globals
    log_config_vars()

    # Initialize Layout
    layout.layout()

    # Run Server
    conf = get_config_vars()
    app.run_server(
        debug=debug,
        host=conf["WEB_SERVER_HOST"],
        port=conf["WEB_SERVER_PORT"],
        # useful dev settings (these are enabled automatically when debug=True)
        dev_tools_silence_routes_logging=True,
        use_reloader=True,
        dev_tools_hot_reload=True,
    )


if __name__ == "__main__":
    # Parse Args
    parser = argparse.ArgumentParser()
    parser.add_argument("-l", "--log", default="INFO", help="the output logging level")
    parser.add_argument("--debug", default=False, action="store_true")
    args = parser.parse_args()

    # Log
    if args.debug:
        coloredlogs.install(level="DEBUG")
    else:
        coloredlogs.install(level=args.log.upper())
    logging.warning(args)

    # Go
    main(args.debug)
