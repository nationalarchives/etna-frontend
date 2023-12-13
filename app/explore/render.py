import math

from app.lib import (
    page_children,
    page_children_paginated,
    page_details,
    pagination_list,
)
from app.wagtail import breadcrumbs
from flask import current_app, render_template, request


def render_explore_page(page_data):
    page_type = page_data["meta"]["type"]
    current_app.logger.debug(f"Page type {page_type} requested")
    if page_type == "articles.ArticleIndexPage":
        return article_index_page(page_data)
    if page_type == "articles.ArticlePage":
        return article_page(page_data)
    if (
        page_type == "collections.TopicExplorerIndexPage"
        or page_type == "collections.TimePeriodExplorerIndexPage"
    ):
        return category_index_page(page_data)
    if (
        page_type == "collections.TopicExplorerPage"
        or page_type == "collections.TimePeriodExplorerPage"
    ):
        return categories_page(page_data)
    if page_type == "articles.RecordArticlePage":
        return record_article_page(page_data)
    if page_type == "articles.FocusedArticlePage":
        return focused_article_page(page_data)
    if page_type == "collections.HighlightGalleryPage":
        return highlight_gallery_page(page_data)
    current_app.logger.error(f"Template for {page_type} not handled")
    return render_template("errors/page-not-found.html"), 404


def category_index_page(page_data):
    try:
        children_data = page_children(page_data["id"])
        all_children = [
            page_details(child["id"]) for child in children_data["items"]
        ]
    except ConnectionError:
        return render_template("errors/api.html"), 502
    children = [
        {
            "id": child["id"],
            "title": child["title"],
            "url": child["meta"]["html_url"],
            "teaser": child["teaser_text"],
            "image": child["teaser_image_jpg"],
        }
        for child in all_children
    ]
    return render_template(
        "explore/category-index.html",
        breadcrumbs=breadcrumbs(page_data["id"]),
        data=page_data,
        children=children,
    )


def categories_page(page_data):
    # TODO

    try:
        children_data = page_children(page_data["id"])
        all_children = [
            page_details(child["id"]) for child in children_data["items"]
        ]
    except ConnectionError:
        return render_template("errors/api.html"), 502
    children = [
        {
            "id": child["id"],
            "title": child["title"],
            "url": child["meta"]["html_url"],
            "teaser": child["teaser_text"],
            "image": child["teaser_image_jpg"],
        }
        for child in all_children
    ]
    return render_template(
        "explore/category.html",
        breadcrumbs=breadcrumbs(page_data["id"]),
        data=page_data,
        children=children,
    )


def article_index_page(page_data):
    children_per_page = 12
    page = int(request.args.get("page")) if "page" in request.args else 1
    try:
        children_data = page_children_paginated(
            page_data["id"], page, children_per_page
        )
    except ConnectionError:
        return render_template("errors/api.html"), 502
    pages = math.ceil(children_data["meta"]["total_count"] / children_per_page)
    if page > pages:
        return render_template("errors/page-not-found.html"), 404
    try:
        children = [
            page_details(child["id"]) for child in children_data["items"]
        ]
        featured_article = page_details(page_data["featured_article"]["id"])
        featured_pages = [
            page_details(featured_page_id)
            for featured_page_id in page_data["featured_pages"][0]["value"][
                "items"
            ]
        ]
    except ConnectionError:
        return render_template("errors/api.html"), 502
    return render_template(
        "explore/stories.html",
        breadcrumbs=breadcrumbs(page_data["id"]),
        data=page_data,
        children=children,
        featured_article=featured_article,
        featured_pages=featured_pages,
        pagination_list=pagination_list(page, pages, 1, 1),
        page=page,
        pages=pages,
    )


def article_page(page_data):
    return render_template(
        "explore/article.html",
        breadcrumbs=breadcrumbs(page_data["id"]),
        data=page_data,
    )


def record_article_page(page_data):
    return render_template(
        "explore/record-article.html",
        breadcrumbs=breadcrumbs(page_data["id"]),
        data=page_data,
    )


def focused_article_page(page_data):
    return render_template(
        "explore/focused-article.html",
        breadcrumbs=breadcrumbs(page_data["id"]),
        data=page_data,
    )


def highlight_gallery_page(page_data):
    return render_template(
        "explore/highlight-gallery.html",
        breadcrumbs=breadcrumbs(page_data["id"]),
        data=page_data,
    )
