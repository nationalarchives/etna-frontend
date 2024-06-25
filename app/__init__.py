# import base64
# import hashlib
import logging

import sentry_sdk
from app.lib import cache
from app.lib.context_processor import (
    cookie_preference,
    merge_dict,
    merge_dict_if,
    now_iso_8601,
    pretty_date_range,
)
from app.lib.template_filters import (
    headings_list,
    iso_date,
    pretty_date,
    pretty_number,
    remove_all_whitespace,
    replace_ext_ref,
    replace_ref,
    slugify,
    tna_html,
    url_encode,
)
from flask import Flask
from flask_talisman import Talisman
from jinja2 import ChoiceLoader, PackageLoader


def create_app(config_class):
    app = Flask(__name__, static_url_path="/static")
    app.config.from_object(config_class)

    if app.config["SENTRY_DSN"]:
        sentry_sdk.init(
            dsn=app.config["SENTRY_DSN"],
            environment=app.config["ENVIRONMENT"],
            release=(
                f"ds-etna-frontend@{app.config['BUILD_VERSION']}"
                if app.config["BUILD_VERSION"]
                else ""
            ),
            sample_rate=app.config["SENTRY_SAMPLE_RATE"],
            traces_sample_rate=app.config["SENTRY_SAMPLE_RATE"],
            profiles_sample_rate=app.config["SENTRY_SAMPLE_RATE"],
        )

    gunicorn_error_logger = logging.getLogger("gunicorn.error")
    app.logger.handlers.extend(gunicorn_error_logger.handlers)
    app.logger.setLevel(gunicorn_error_logger.level or "DEBUG")

    cache.init_app(
        app,
        config={
            "CACHE_TYPE": app.config["CACHE_TYPE"],
            "CACHE_DEFAULT_TIMEOUT": app.config["CACHE_DEFAULT_TIMEOUT"],
            "CACHE_IGNORE_ERRORS": app.config["CACHE_IGNORE_ERRORS"],
            "CACHE_DIR": app.config["CACHE_DIR"],
        },
    )

    # scripts = [
    #     "app/static/main.min.js",
    #     "app/static/analytics.min.js",
    #     "app/static/article.min.js",
    # ]
    # script_hases = []
    # for script in scripts:
    #     # https://codeberg.org/fbausch/csp-hash/src/branch/main/src/csp-hash.py
    #     with open(script, "r") as f:
    #         file_contents = f.read()
    #         file_contents = file_contents.replace("\r", "")
    #         sha = base64.b64encode(
    #             hashlib.sha256(file_contents.encode("utf-8")).digest()
    #         ).decode("utf-8")
    #         entry = f"'sha256-{sha}'"
    #         if entry not in script_hases:
    #             script_hases.append(f"'sha256-{sha}'")
    # print(script_hases)

    Talisman(
        app,
        content_security_policy={
            "default-src": "'self'",
            "base-uri": "'none'",
            "object-src": "'none'",
            "img-src": app.config["CSP_IMG_SRC"],
            "script-src": app.config["CSP_SCRIPT_SRC"],
            "script-src-elem": app.config["CSP_SCRIPT_SRC_ELEM"],
            "style-src": app.config["CSP_STYLE_SRC"],
            "font-src": app.config["CSP_FONT_SRC"],
            "connect-src": app.config["CSP_CONNECT_SRC"],
            "media-src": app.config["CSP_MEDIA_SRC"],
            "worker-src": app.config["CSP_WORKER_SRC"],
        },
        # content_security_policy_nonce_in=["script-src", "style-src"],
        feature_policy={
            "camera": "'none'",
            "fullscreen": "'self'",
            "geolocation": "'none'",
            "microphone": "'none'",
            "screen-wake-lock": "'none'",
        },
        force_https=app.config["FORCE_HTTPS"],
        frame_options="ALLOW-FROM",
        frame_options_allow_from=app.config["FRAME_DOMAIN_ALLOW"],
    )

    @app.after_request
    def apply_extra_headers(response):
        response.headers["X-Permitted-Cross-Domain-Policies"] = "none"
        response.headers["Cross-Origin-Embedder-Policy"] = "credentialless"
        response.headers["Cross-Origin-Opener-Policy"] = "same-origin"
        response.headers["Cross-Origin-Resource-Policy"] = "same-origin"
        response.headers["Cache-Control"] = (
            f"public, max-age={app.config['CACHE_HEADER_DURATION']}"
        )
        return response

    app.jinja_env.trim_blocks = True
    app.jinja_env.lstrip_blocks = True
    app.jinja_loader = ChoiceLoader(
        [
            PackageLoader("app"),
            PackageLoader("tna_frontend_jinja"),
        ]
    )

    app.add_template_filter(tna_html)
    app.add_template_filter(slugify)
    app.add_template_filter(pretty_date)
    app.add_template_filter(iso_date)
    app.add_template_filter(pretty_number)
    app.add_template_filter(headings_list)
    app.add_template_filter(replace_ref)
    app.add_template_filter(replace_ext_ref)
    app.add_template_filter(remove_all_whitespace)
    app.add_template_filter(url_encode)

    @app.context_processor
    def context_processor():
        return dict(
            merge_dict=merge_dict,
            merge_dict_if=merge_dict_if,
            cookie_preference=cookie_preference,
            now_iso_8601=now_iso_8601,
            pretty_date_range=pretty_date_range,
            app_config=app.config,
        )

    from .about import bp as about_bp
    from .catalogue import bp as catalogue_bp
    from .help import bp as help_bp
    from .legal import bp as legal_bp
    from .main import bp as site_bp
    from .search import bp as search_bp
    from .wagtail import bp as wagtail_bp

    app.register_blueprint(site_bp)
    app.register_blueprint(legal_bp, url_prefix="/legal")
    app.register_blueprint(help_bp, url_prefix="/help")
    app.register_blueprint(about_bp, url_prefix="/about")
    app.register_blueprint(search_bp, url_prefix="/search")
    app.register_blueprint(catalogue_bp, url_prefix="/catalogue")
    app.register_blueprint(wagtail_bp)

    return app
