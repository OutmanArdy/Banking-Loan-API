# SAFE RUN NOTES
- Create isolated environment (docker or VM).
- Install deps: python -m venv venv && source venv/bin/activate && pip install -r requirements.txt
- Run semgrep: pip install semgrep ; semgrep --config semgrep-rules.yml vulnerable_app.py
- Do NOT expose this service to internet.
