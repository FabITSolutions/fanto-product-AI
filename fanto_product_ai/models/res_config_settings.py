# -*- coding: utf-8 -*-
from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    fanto_ai_provider = fields.Selection(
        selection=[
            ("anthropic", "Anthropic (Claude)"),
            ("openai", "OpenAI (GPT-4)"),
            ("groq", "Groq (Free - Llama)"),
            ("ollama", "Ollama (Free)"),
        ],
        string="Default AI Provider",
        default="ollama",
        config_parameter="fanto_product_ai.provider",
    )

    # ── API Keys ─────────────────────────────────────────────────────────────
    fanto_anthropic_api_key = fields.Char(
        string="Anthropic API Key",
        config_parameter="fanto_product_ai.anthropic_api_key",
    )
    fanto_openai_api_key = fields.Char(
        string="OpenAI API Key",
        config_parameter="fanto_product_ai.openai_api_key",
    )
    fanto_groq_api_key = fields.Char(
        string="Groq API Key",
        config_parameter="fanto_product_ai.groq_api_key",
    )
    fanto_ollama_api_key = fields.Char(
        string="Ollama API Key",
        config_parameter="fanto_product_ai.ollama_api_key",
    )

    # ── Default model names (overridable) ────────────────────────────────────
    fanto_anthropic_model = fields.Char(
        string="Claude Model",
        default="claude-sonnet-4-20250514",
        config_parameter="fanto_product_ai.anthropic_model",
    )
    fanto_openai_model = fields.Char(
        string="OpenAI Model",
        default="gpt-4o",
        config_parameter="fanto_product_ai.openai_model",
    )
    fanto_groq_model = fields.Char(
        string="Groq Model",
        default="llama-3.3-70b-versatile",
        config_parameter="fanto_product_ai.groq_model",
    )
    fanto_ollama_model = fields.Char(
        string="Ollama Model",
        default="llama3.2",
        config_parameter="fanto_product_ai.ollama_model",
    )
