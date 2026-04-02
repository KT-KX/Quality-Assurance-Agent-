# **QA Agent and Issue Resolution Workflow**



This n8n workflow automates the software lifecycle for vision algorithms. It monitors GitHub issues, uses Ollama to generate code fixes and test cases, and runs Pytest to verify the solution before notifying the team.



## **Prerequisites**

* n8n installed (Desktop or Docker).
* ngrok installed for local webhook tunneling.
* Python 3.13(or below) with `pytest` installed (`pip install pytest`).
* Ollama running locally with the required model (gwen2.5 coder).





## **Setup \& Execution**



1. Start the Webhook Tunnel

Since GitHub needs to send data to your local n8n instance, you must expose your local port (default 5678) to the internet.



```bash

ngrok http 5678

```



Copy the `Forwarding` URL provided by ngrok (e.g., `https://abc-123.ngrok-free.app`).\*



2\. Configure n8n Environment

Set your Webhook URL environment variable so n8n uses the ngrok link for the GitHub trigger.



```bash

export WEBHOOK\_URL=https://your-ngrok-link.ngrok-free.app

n8n start

```



## **Workflow Configuration**

1\.  Import Workflow: Import the `Group\_4.json` file into your n8n canvas.

2\.  GitHub Credentials:  Open the GitHub Trigger node.

&#x20;   Create a new credential using a Personal Access Token (PAT) with `repo` and `admin:repo\_hook` permissions.

3\.  Python Path: Locate the \*Execute Command\* node (labeled "Run Pytest").

&#x20;   \* Update the command path to match your local Python environment. 

&#x20;   \* Example: `C:\\Users\\Name\\AppData\\Local\\Programs\\Python\\Python39\\python.exe -m pytest` or simply `/usr/bin/python3 -m pytest`.

4\.  Ollama Connection: Ensure the Ollama Chat Model nodes are pointing to your local Ollama instance (usually `http://localhost:11434`).





## **How to Test**



1. Activate: Click the "Executable" toggle in the top right of the n8n interface.



2\. Trigger: Go to your GitHub repository and Open a New Issue.



Tip: Include code snippets or specific error logs in the issue description to give the AI context. 



3\. Monitor: Watch the n8n execution log.



* Step 1: The agent triages the issue.
* Step 2: An email notification is sent via Gmail.
* Step 3: The agent generates 5 Pytest cases and executes them.
* Step 4: You receive a final summary email with the proposed fix.



## Troubleshooting

* Webhook Failures: Ensure the Webhook URL in n8n settings matches your current ngrok URL. GitHub hooks fail if the URL changes after a restart.
* Python Permissions: Ensure the user running n8n has permission to execute scripts in the specified Python path.
* Ollama Timeout: If the AI is slow, increase the timeout settings in the AI Agent node.

