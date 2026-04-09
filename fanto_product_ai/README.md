# Fanto AI Product Description Generator

Generate compelling e-commerce product descriptions using AI directly within Odoo.

## Features

- **Multiple AI Providers**: Choose from 4 different AI providers:
  - **Anthropic Claude** - Premium AI with excellent reasoning
  - **OpenAI GPT-4** - Industry-leading AI model
  - **Groq (Free)** - Fast, free AI inference
  - **Ollama (Free)** - Run AI locally for complete privacy

- **Customizable Output**:
  - Select output language (10+ languages supported)
  - Choose tone: Professional, Friendly, Luxury, or Technical
  - Add extra context for specific requirements

- **Preview Before Saving**: Review generated descriptions before applying them to products

- **Easy Integration**: Access AI description generation directly from product form

## Installation

1. Download or clone this module to your Odoo addons directory
2. Update apps list in Odoo
3. Install "Fanto AI Product Description Generator"

## Configuration

1. Go to **Settings > General Settings**
2. Find the **Fanto AI** section
3. Configure your preferred AI provider:
   - Enter API key for your chosen provider
   - Optionally customize the default model

### Getting API Keys

| Provider | Website | Notes |
|----------|---------|-------|
| Groq | [console.groq.com](https://console.groq.com) | Free tier available, no credit card required |
| Ollama | [ollama.com](https://ollama.com) | Cloud API key required |
| Anthropic | [console.anthropic.com](https://console.anthropic.com) | Paid service |
| OpenAI | [platform.openai.com](https://platform.openai.com) | Paid service |

### Recommended Free Setup

For a completely free setup, use **Groq** with the default model `llama-3.3-70b-versatile`.

## Usage

1. Open any product in Odoo
2. Click the **"AI Description"** button in the action box
3. Select your preferred AI provider
4. Choose language and tone
5. Optionally add extra context/instructions
6. Click **"Generate Description"**
7. Review the generated description
8. Click **"Save to Product"** or **"Regenerate"** if needed

## Supported Languages

- English
- French (Français)
- German (Deutsch)
- Spanish (Español)
- Italian (Italiano)
- Dutch (Nederlands)
- Portuguese (Português)
- Arabic (العربية)
- Chinese (中文)
- Japanese (日本語)

## Requirements

- Odoo 18.0
- Internet connection (for cloud AI providers)
- API key from chosen AI provider

## Support

For issues or feature requests, please contact:
- Website: [fanto.fr](https://www.fanto.fr)
- Email: support@fanto.fr

## License

This module is licensed under **LGPL-3**.

## Authors

- **Fanto** - [fanto.fr](https://www.fanto.fr)
