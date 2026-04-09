# -*- coding: utf-8 -*-
import json
import logging
import requests

from odoo import _, api, fields, models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

LANGUAGES = [
    ("en", "English"),
    ("fr", "French (Français)"),
    ("de", "German (Deutsch)"),
    ("es", "Spanish (Español)"),
    ("it", "Italian (Italiano)"),
    ("nl", "Dutch (Nederlands)"),
    ("pt", "Portuguese (Português)"),
    ("ar", "Arabic (العربية)"),
    ("zh", "Chinese (中文)"),
    ("ja", "Japanese (日本語)"),
]


def _get_param(env, key, default=""):
    return env["ir.config_parameter"].sudo().get_param(key, default)


class ProductAiDescriptionWizard(models.TransientModel):
    _name = "product.ai.description.wizard"
    _description = "AI Product Description Generator"

    product_id = fields.Many2one(
        "product.template",
        string="Product",
        required=True,
        readonly=True,
    )
    product_name = fields.Char(related="product_id.name", readonly=True)
    product_categ = fields.Many2one(related="product_id.categ_id", readonly=True)

    language = fields.Selection(
        selection=LANGUAGES,
        string="Output Language",
        required=True,
        default="en",
    )
    provider = fields.Selection(
        selection=[
            ("anthropic", "Anthropic (Claude)"),
            ("openai", "OpenAI (GPT-4)"),
            ("groq", "Groq (Free - Llama)"),
            ("ollama", "Ollama (Free)"),
        ],
        string="AI Provider",
        required=True,
    )
    tone = fields.Selection(
        selection=[
            ("professional", "Professional"),
            ("friendly", "Friendly & Engaging"),
            ("luxury", "Luxury / Premium"),
            ("technical", "Technical / Detailed"),
        ],
        string="Tone",
        default="professional",
        required=True,
    )
    extra_context = fields.Text(
        string="Extra Instructions",
        placeholder="e.g. Highlight eco-friendly materials, mention warranty...",
    )

    state = fields.Selection(
        selection=[("draft", "Configure"), ("preview", "Preview")],
        default="draft",
    )

    generated_html = fields.Html(
        string="Generated Description",
        sanitize=False,
    )

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        res["provider"] = _get_param(
            self.env, "fanto_product_ai.provider", "ollama"
        )
        return res

    def _build_prompt(self):
        self.ensure_one()
        product = self.product_id
        lang_label = dict(LANGUAGES).get(self.language, self.language)
        tone_label = dict(self._fields["tone"].selection).get(self.tone, self.tone)

        # Gather available product info
        lines = [f"Product name: {product.name}"]
        if product.categ_id:
            lines.append(f"Category: {product.categ_id.complete_name}")
        if product.description:
            lines.append(f"Internal notes: {product.description}")
        if product.description_sale:
            lines.append(f"Sales description: {product.description_sale}")
        if product.list_price:
            lines.append(f"Price: {product.list_price} {product.currency_id.name}")
        if self.extra_context:
            lines.append(f"Additional context: {self.extra_context}")

        product_info = "\n".join(lines)

        prompt = f"""Write a compelling, SEO-friendly e-commerce product description in **{lang_label}**.

Tone: {tone_label}
Output: ONLY valid HTML (use <p>, <ul>, <li>, <strong> tags only). NO explanation, NO reasoning, NO preamble, NO markdown, NO code fences. Start directly with <p> tag.

Product:
{product_info}

HTML:"""
        return prompt

    def _clean_html_response(self, html):
        html = html.strip()
        if html.startswith("```html"):
            html = html[7:]
        elif html.startswith("```"):
            html = html[3:]
        if html.endswith("```"):
            html = html[:-3]
        
        idx = html.lower().find("<html")
        if idx > 0:
            html = html[idx:]
        
        idx = html.lower().find("<body")
        if idx > 0 and html.lower().find("<html") < 0:
            html = html[idx:]
        
        idx = html.lower().find("<p")
        if idx > 0:
            html = html[idx:]
        
        html = html.strip()
        return html

    # ── AI call: Anthropic ────────────────────────────────────────────────────
    def _call_anthropic(self, prompt):
        api_key = _get_param(self.env, "fanto_product_ai.anthropic_api_key")
        if not api_key:
            raise UserError(_("Anthropic API key is not configured. Please set it in Settings."))
        model = _get_param(
            self.env, "fanto_product_ai.anthropic_model", "claude-sonnet-4-20250514"
        )
        url = "https://api.anthropic.com/v1/messages"
        payload = json.dumps({
            "model": model,
            "max_tokens": 1024,
            "messages": [{"role": "user", "content": prompt}],
        })
        headers = {
            "Content-Type": "application/json",
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01",
        }

        try:
            response = requests.post(url, headers=headers, data=payload, timeout=60)
            if response.status_code != 200:
                _logger.error("Anthropic API error %s: %s", response.status_code, response.text)
                raise UserError(_("Anthropic API error %s: %s") % (response.status_code, response.text))
            data = response.json()
            return data["content"][0]["text"].strip()
        except requests.exceptions.Timeout:
            _logger.error("Anthropic API timeout")
            raise UserError(_("Anthropic API request timed out. Please try again."))
        except Exception as e:
            _logger.error("Anthropic call failed: %s", e)
            raise UserError(_("Failed to contact Anthropic API: %s") % str(e))

    # ── AI call: OpenAI ───────────────────────────────────────────────────────
    def _call_openai(self, prompt):
        api_key = _get_param(self.env, "fanto_product_ai.openai_api_key")
        if not api_key:
            raise UserError(_("OpenAI API key is not configured. Please set it in Settings."))
        model = _get_param(self.env, "fanto_product_ai.openai_model", "gpt-4o")
        url = "https://api.openai.com/v1/chat/completions"
        payload = json.dumps({
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 1024,
        })
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        }

        try:
            response = requests.post(url, headers=headers, data=payload, timeout=60)
            if response.status_code != 200:
                _logger.error("OpenAI API error %s: %s", response.status_code, response.text)
                raise UserError(_("OpenAI API error %s: %s") % (response.status_code, response.text))
            data = response.json()
            return data["choices"][0]["message"]["content"].strip()
        except requests.exceptions.Timeout:
            _logger.error("OpenAI API timeout")
            raise UserError(_("OpenAI API request timed out. Please try again."))
        except Exception as e:
            _logger.error("OpenAI call failed: %s", e)
            raise UserError(_("Failed to contact OpenAI API: %s") % str(e))

    # ── AI call: Groq (Free tier) ─────────────────────────────────────────────
    def _call_groq(self, prompt):
        api_key = _get_param(self.env, "fanto_product_ai.groq_api_key")
        if not api_key:
            raise UserError(_("Groq API key is not configured. Get free key at console.groq.com."))
        model = _get_param(self.env, "fanto_product_ai.groq_model", "llama-3.3-70b-versatile")

        url = "https://api.groq.com/openai/v1/chat/completions"
        payload = json.dumps({
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 1024,
        })
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        }

        try:
            response = requests.post(url, headers=headers, data=payload, timeout=60)
            if response.status_code != 200:
                _logger.error("Groq API error %s: %s", response.status_code, response.text)
                raise UserError(_("Groq API error %s: %s") % (response.status_code, response.text))
            data = response.json()
            return data["choices"][0]["message"]["content"].strip()
        except requests.exceptions.Timeout:
            _logger.error("Groq API timeout")
            raise UserError(_("Groq API request timed out. Please try again."))
        except Exception as e:
            _logger.error("Groq call failed: %s", e)
            raise UserError(_("Failed to contact Groq API: %s") % str(e))

    # ── AI call: Ollama (Cloud API) ───────────────────────────────────────────
    def _call_ollama(self, prompt):
        api_key = _get_param(self.env, "fanto_product_ai.ollama_api_key")
        if not api_key:
            raise UserError(_("Ollama API key is not configured. Get key at ollama.com."))
        model = _get_param(self.env, "fanto_product_ai.ollama_model", "llama3.2")

        url = "https://ollama.com/api/chat"
        payload = json.dumps({
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "stream": False,
        })
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        }

        try:
            response = requests.post(url, headers=headers, data=payload, timeout=120)
            if response.status_code != 200:
                _logger.error("Ollama API error %s: %s", response.status_code, response.text)
                raise UserError(_("Ollama API error %s: %s") % (response.status_code, response.text))
            data = response.json()
            return data["message"]["content"].strip()
        except requests.exceptions.Timeout:
            _logger.error("Ollama API timeout")
            raise UserError(_("Ollama API request timed out. Please try again."))
        except Exception as e:
            _logger.error("Ollama call failed: %s", e)
            raise UserError(_("Failed to contact Ollama API: %s") % str(e))

    # ── Actions ───────────────────────────────────────────────────────────────
    def action_generate(self):
        """Call AI, store result, switch to preview state."""
        self.ensure_one()
        prompt = self._build_prompt()

        if self.provider == "anthropic":
            html = self._call_anthropic(prompt)
        elif self.provider == "openai":
            html = self._call_openai(prompt)
        elif self.provider == "groq":
            html = self._call_groq(prompt)
        elif self.provider == "ollama":
            html = self._call_ollama(prompt)
        else:
            raise UserError(_("Unknown AI provider: %s") % self.provider)

        html = self._clean_html_response(html)
        self.write({"generated_html": html, "state": "preview"})

        # Keep wizard open
        return {
            "type": "ir.actions.act_window",
            "res_model": self._name,
            "res_id": self.id,
            "view_mode": "form",
            "target": "new",
        }

    def action_regenerate(self):
        """Go back to draft to tweak options."""
        self.ensure_one()
        self.write({"state": "draft", "generated_html": False})
        return {
            "type": "ir.actions.act_window",
            "res_model": self._name,
            "res_id": self.id,
            "view_mode": "form",
            "target": "new",
        }

    def action_save(self):
        """Write generated HTML to product's description_ecommerce field."""
        self.ensure_one()
        if not self.generated_html:
            raise UserError(_("Nothing to save. Please generate a description first."))
        self.product_id.sudo().write({"description_ecommerce": self.generated_html})
        return {"type": "ir.actions.act_window_close"}
