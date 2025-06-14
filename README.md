# 🚀 Simple AI Reviewer

<div align="center">
  <img src="ai-reviewer2.png"/>
</div>

## 📝 Description

The **Simple AI Reviewer** is designed to assist developers working alone. It aims to highlight potential issues within a codebase, offer suggestions for improvements, or simply provide a fresh perspective.   

⚠️ **Important Note**:  
Its outputs may be insightful, misleading, or entirely useless — treat its suggestions with a healthy dose of skepticism. This tool is intended as a **supplement to your own expertise**, not a replacement for it.

## 🌐 Compatibility with Git Hosting

Currently supports:  
* **Gitea**
* **Github**

## 🛠 Getting Started

### 🔧 General preparation

**1️⃣ Clone the repository**
```bash
git clone https://github.com/amest/simple-ai-reviewer.git
```

**2️⃣ Configure Git hosting:**
- If using Gitea - [configure Gitea ](#gitea)
- If using Github - [configure Github ](#github)

### 🐳 Docker

To run the application using Docker, follow these steps:

1. Configure the application using environment variables. You can find a sample configuration in the [`compose.yml`](compose.yml) file. For all available configuration options, see the [Application configurations](#application) section or the [appsettings.json](appsettings.json) file.

2. Build and start the application using docker compose:
```bash
docker-compose up --build
```

This will:
- Build the Docker image
- Start the application container
- Expose the service on the configured port (default: 8888)

### Manual without docker

To run the application without Docker, follow these steps:

1. Configure the application by editing the [appsettings.json](appsettings.json) file. For detailed configuration options with comments, see the [Application configurations](#application) section.

2. Install the required dependencies:
```bash
pip install -r requirements.txt
```

3. Run the service:
```bash
python main.py
```

The service will start and listen on the configured host and port (default: localhost:8888).

### ⚙️ Configuration

#### Gitea
- Create user (example: `ai-reviewer`) **_Optional_**
- Create Token for user
- Add this user to your repositories as co-author **_Optional if user created_**
- Configure webhook in your Gitea repository. 
  - Endpoint: `https://your-domain-with-running-service/webhook/gitea?token=TOKEN_FROM_APPSETTINGS`
  - Content type: `application/json`
  - Select webhook events: 'Pull Request Comment' (required) and/or 'Issue Comment' (optional)

#### Github
- Create user (example: `{generated-username}-ai-reviewer`) **_Optional_**
- Create Token for user
  - Contents: Read-only
  - Issues: Read and write
  - Pull requests: Read and write
- Add this user to your repositories as co-author **_Optional if user created_**
- Configure webhook in your Github repository. 
  - Endpoint: `https://your-domain-with-running-service/webhook/github?token=TOKEN_FROM_APPSETTINGS`
  - Content type: `application/json`
  - Select only one webhook event: **Issue comments**

#### Application

| Section  | Parameter                 | Description                                                                                                                        |
| -------- | ------------------------- | ---------------------------------------------------------------------------------------------------------------------------------- |
| `web`    | `host`                    | bind address                                                                                                                       |
| `web`    | `port`                    | bind port                                                                                                                          |
| `web`    | `token`                   | authorization token for connection webhooks securely                                                                               |
| `gitea`  | `base_url`                | your gitea url                                                                                                                     |
| `gitea`  | `token`                   | personal access token for access to api                                                                                            |
| `gitea`  | `allowed_emails`          | email list (separated by `;` or `,`) with users, who can run review                                                                |
| `github` | `token`                   | personal access token for access to api                                                                                            |
| `github` | `allowed_logins`          | logins list (separated by `;` or `,`) with users, who can run review                                                               |
| `llm`    | `type`                    | provider type: `ollama`, `openai-compatible`                                                                                       |
| `llm`    | `base_url`                | url to ollama or openai compatible server                                                                                          |
| `llm`    | `model`                   | model name for using in service                                                                                                    |
| `llm`    | `token`                   | api token for connect to openai-compatible server                                                                                  |
| `review` | `language`                | prompt language: `ru`, `en`                                                                                                        |
| `review` | `ignore_files`            | list file names (separated by `,`) excluded from review                                                                            |
| `review` | `review_as_comments`      | flag for enable/disable process review and send as simple comment in Pull Request                                                  |
| `review` | `review_as_conversations` | flag for enable/disable process review and send as conversations to files in pull request (comments applied to files in `Changes`) |

## 🎯 Example Usage

1. Create a Pull Request in your Gitea/Github repository
2. Write comment in PR with text `/start_review`
3. 🤖 The AI Reviewer will automatically analyze the changes and post comments
4. 🔍 Review the suggestions and apply them as needed

## 📌 Notes

*   This is a basic implementation and may require adjustments based on your project's specific needs.
*   Consider providing feedback to help improve the accuracy and usefulness of the AI reviewer.
*   Remember to validate the reviewer's findings and use your own judgment.
*   **❗Some file reviews may miss lines to which the comment pertains (while this feature exists, it depends on the model used)**
*   **❗In principle, a lot depends on the models used to conduct the review. Testing was done with the following models:**
    *   `Ollama`
        *   `Gemma3:1b` - Weak and suitable for very simple Pull Requests, but in general it finds and highlights useful things. In the per-file review mode - useless
        *   `Gemma3:4b` - Relatively well reviews in the regular comments mode (as far as possible for a small model), but in the per-file review mode it poorly specifies files and lines; It can link all comments to one file. Per-file mode is not even worth trying
    *   `Openai-compatible`
        *   `deepseek-chat` - Not bad reviews in the regular comments mode. In the per-file review mode it also successfully links comments/advice/questions to files, but sometimes (or more precisely in 50%) it misses the exact diff line, but you can't get used to it
