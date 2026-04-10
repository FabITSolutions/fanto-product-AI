# -*- coding: utf-8 -*-
{
    "name": "Fanto AI Product Description Generator",
    "summary": "Generate product e-commerce descriptions using AI",
    "description": """
        AI-powered description generator for product e-commerce pages.
        Supports Anthropic Claude, OpenAI GPT-4, Groq (free), and Ollama (free).
        Features: language selection, tone options, preview before saving.
    """,
    "author": "Fanto",
    "website": "https://www.fanto.fr",
    "category": "Sales/Products",
    "version": "19.0.1.0.0",
    "depends": ["product", "website_sale"],
    "data": [
        "security/ir.model.access.csv",
        "data/res_config_settings_data.xml",
        "views/res_config_settings_views.xml",
        "wizard/product_ai_description_wizard_views.xml",
        "views/product_views.xml",
    ],
    'images': [
        'static/description/banner.png',
    ],
    "installable": True,
    "application": False,
    "license": "LGPL-3",
}
