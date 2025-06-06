# Simple AI Reviewer

## Description

The Simple AI Reviewer is designed to assist developers working alone. It aims to highlight potential issues within a codebase, offer suggestions for improvements, or simply provide a fresh perspective.   
It's important to note that its outputs may be insightful, misleading, or entirely useless - treat its suggestions with a healthy dose of skepticism.  This tool is intended as a supplement to your own expertise, not a replacement for it.

## Technologies (Stack)
*   Python 3.9+
*   Flask (web framework)
*   Requests (HTTP client)
*   OpenAI (AI integration)
*   py_configuration_builder (configuration management)
*   py_simple_container (dependency injection)
*   Docker (containerization)
*   Gitea (git hosting integration)

## Compatibility with git hosting

At now, supports only Gitea

## Getting Started

1. Clone the repository:
   ```bash
   git clone https://github.com/amest/simple-ai-reviewer.git
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Configure the application:
   - Configure Gitea:
     - Create user (example: `ai-reviewer`)
     - Create Token for user
     - Add this user to your repositories as co-author
     - Configure webhook in your Gitea repository. 
       - Endpoint: `https://your-domain-with-running-service/webhook/gitea?token=TOKEN_FROM_APPSETTINGS`
       - Select only one webhook event: Comments in pull request
   - Edit `appsettings.json` with your Gitea credentials (base url and token from `ai-reviewer` user) and AI settings.
   See section `Configuration`

4. Run the service:
   ```bash
   python main.py
   ```

   Or using Docker:
   ```bash
   docker build -t ai-reviewer .
   docker run -p 8888:8888 ai-reviewer
   ```
### Configuration
* web - section for configuring api
  * host - bind address
  * post - bind port
  * token - authorization token for connection webhooks securely
* gitea - section for configuring gitea api
  * base_url - your gitea url
  * token - personal access token for access to api
* llm - section for configuring LLM provider
  * type - provider type: `ollama`, `openai-compatible`
  * base_url - url to ollama or openai compatible server
  * model - model name for using in service
  * token - api token for connect to openai-compatible server
* review - section for configuring review behavior
  * language - prompt language: `ru`, `en`

## Example Usage

1. Create a Pull Request in your Gitea repository
2. Write comment in PR with text `/start_review`
3. The AI Reviewer will automatically analyze the changes and post comments
4. Review the suggestions and apply them as needed

## Notes

*   This is a basic implementation and may require adjustments based on your project's specific needs.
*   Consider providing feedback to help improve the accuracy and usefulness of the AI reviewer.
*   Remember to validate the reviewer's findings and use your own judgment.
