"""REST API server for analyzer."""
import json
import logging
import os
from logging.config import fileConfig
from pathlib import Path
from typing import Tuple
from datetime import datetime
from flask import Flask, request, jsonify, Response
from werkzeug.exceptions import HTTPException

from presidio_analyzer.analyzer_engine import AnalyzerEngine
from presidio_analyzer.analyzer_request import AnalyzerRequest

DEFAULT_PORT = "3000"

LOGGING_CONF_FILE = "logging.ini"

WELCOME_MESSAGE = r"""
 _______  _______  _______  _______ _________ ______  _________ _______
(  ____ )(  ____ )(  ____ \(  ____ \\__   __/(  __  \ \__   __/(  ___  )
| (    )|| (    )|| (    \/| (    \/   ) (   | (  \  )   ) (   | (   ) |
| (____)|| (____)|| (__    | (_____    | |   | |   ) |   | |   | |   | |
|  _____)|     __)|  __)   (_____  )   | |   | |   | |   | |   | |   | |
| (      | (\ (   | (            ) |   | |   | |   ) |   | |   | |   | |
| )      | ) \ \__| (____/\/\____) |___) (___| (__/  )___) (___| (___) |
|/       |/   \__/(_______/\_______)\_______/(______/ \_______/(_______)
"""


class Server:
    """HTTP Server for calling Presidio Analyzer."""

    def __init__(self):
        fileConfig(Path(Path(__file__).parent, LOGGING_CONF_FILE))
        self.logger = logging.getLogger("presidio-analyzer")
        self.logger.setLevel(os.environ.get("LOG_LEVEL", self.logger.level))
        self.app = Flask(__name__)
        self.logger.info("Starting analyzer engine")
        self.engine = AnalyzerEngine()
        self.logger.info(WELCOME_MESSAGE)

        @self.app.route("/health")
        def health() -> str:
            """Return basic health probe result."""
            return "Presidio Analyzer service is up"

        @self.app.route("/analyze", methods=["POST"])
        def analyze() -> Tuple[str, int]:
            """Execute the analyzer function."""

            # Attempt to read and log the request body
            try:
                request_body = request.get_data(as_text=True)
            except Exception as e:
                request_body = f"Failed to read request body: {str(e)}"
                
            try:
                log_banner = "=" * 80
                current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

                log_message = (
                    f"\n{log_banner}\n"
                    f"REQUEST LOG - {current_time}\n"
                    f"Method: {request.method}\n"
                    f"URL: {request.url}\n"
                    f"Headers: {json.dumps(dict(request.headers), indent=4)}\n"
                    f"Content-Type: {request.content_type}\n"
                    f"Body: {request_body}\n"
                    f"{log_banner}\n"
                )

                self.logger.info(log_message)
                
                text = None
                language = None

                content_type = request.content_type
                self.logger.info(f"Processing content type: {content_type}")

                if content_type.startswith('multipart/form-data'):
                    # Handle file uploads
                    uploaded_file = request.files.get('file')
                    if uploaded_file:
                        text = uploaded_file.read().decode('utf-8')
                    language = request.form.get('language')
                elif content_type == 'application/json':
                    # Handle JSON payload
                    req_data = AnalyzerRequest(request.get_json())
                    text = req_data.text
                    language = req_data.language
                elif content_type == 'application/x-www-form-urlencoded':
                    # Handle application/x-www-form-urlencoded
                    text = request.form.get('text')
                    language = request.form.get('language')

                elif content_type == 'text/plain':
                    # Read raw text
                    text = request.data.decode('utf-8')
                    language = "en" # By default set for text/plain
                else:
                    raise HTTPException(description=f"Unsupported Content-Type: {content_type}")

                if not text:
                    raise Exception("No text provided")

                if not language:
                    raise Exception("No language provided")

                recognizer_result_list = self.engine.analyze(
                    text=text,
                    language=language,
                    correlation_id=req_data.correlation_id if content_type == 'application/json' else None,
                    score_threshold=req_data.score_threshold if content_type == 'application/json' else None,
                    entities=req_data.entities if content_type == 'application/json' else None,
                    return_decision_process=req_data.return_decision_process if content_type == 'application/json' else None,
                    ad_hoc_recognizers=req_data.ad_hoc_recognizers if content_type == 'application/json' else None,
                    context=req_data.context if content_type == 'application/json' else None,
                )

                return Response(
                    json.dumps(
                        recognizer_result_list,
                        default=lambda o: o.to_dict(),
                        sort_keys=True,
                    ),
                    content_type="application/json",
                )
            except TypeError as te:
                error_msg = (
                    f"Failed to parse /analyze request "
                    f"for AnalyzerEngine.analyze(). {te.args[0]}"
                )
                self.logger.error(error_msg)
                return jsonify(error=error_msg), 400

            except HTTPException as e:
                return jsonify(error=e.description), e.code

            except Exception as e:
                self.logger.error(
                    f"A fatal error occurred during execution of "
                    f"AnalyzerEngine.analyze(). {e}"
                )
                return jsonify(error=e.args[0]), 500

        @self.app.route("/recognizers", methods=["GET"])
        def recognizers() -> Tuple[str, int]:
            """Return a list of supported recognizers."""
            language = request.args.get("language")
            try:
                recognizers_list = self.engine.get_recognizers(language)
                names = [o.name for o in recognizers_list]
                return jsonify(names), 200
            except Exception as e:
                self.logger.error(
                    f"A fatal error occurred during execution of "
                    f"AnalyzerEngine.get_recognizers(). {e}"
                )
                return jsonify(error=e.args[0]), 500

        @self.app.route("/supportedentities", methods=["GET"])
        def supported_entities() -> Tuple[str, int]:
            """Return a list of supported entities."""
            language = request.args.get("language")
            try:
                entities_list = self.engine.get_supported_entities(language)
                return jsonify(entities_list), 200
            except Exception as e:
                self.logger.error(
                    f"A fatal error occurred during execution of "
                    f"AnalyzerEngine.supported_entities(). {e}"
                )
                return jsonify(error=e.args[0]), 500

        @self.app.errorhandler(HTTPException)
        def http_exception(e):
            return jsonify(error=e.description), e.code


if __name__ == "__main__":
    port = int(os.environ.get("PORT", DEFAULT_PORT))
    server = Server()
    server.app.run(host="0.0.0.0", port=port)
