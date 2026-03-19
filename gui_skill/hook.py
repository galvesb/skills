#!/usr/bin/env python3
"""
Hook UserPromptSubmit — injeta instruções privadas de skills em tempo real.

Detecta marcadores {{PRIVATE:categoria/skill}} no prompt,
busca o conteúdo real do repositório privado no GitHub
e injeta como contexto antes de enviar ao Claude.
"""
import base64
import json
import os
import re
import sys

try:
    import requests
except ImportError:
    sys.exit(0)

MARKER_RE = re.compile(r"\{\{PRIVATE:([\w/-]+)\}\}")


def fetch_private_skill(path: str) -> str | None:
    token = os.environ.get("SKILLS_GITHUB_TOKEN")
    if not token:
        return None

    repo = os.environ.get("SKILLS_PRIVATE_REPO", "galvesb/skills-private")
    branch = os.environ.get("SKILLS_PRIVATE_BRANCH", "main")
    url = f"https://api.github.com/repos/{repo}/contents/{path}.md"

    try:
        resp = requests.get(
            url,
            headers={
                "Authorization": f"token {token}",
                "Accept": "application/vnd.github.v3+json",
            },
            params={"ref": branch},
            timeout=10,
        )
        resp.raise_for_status()
        content_b64 = resp.json()["content"].replace("\n", "")
        return base64.b64decode(content_b64).decode("utf-8")
    except Exception:
        return None


def main():
    try:
        data = json.loads(sys.stdin.read())
    except Exception:
        sys.exit(0)

    prompt = data.get("prompt", "")
    match = MARKER_RE.search(prompt)

    if not match:
        sys.exit(0)

    skill_path = match.group(1)
    instructions = fetch_private_skill(skill_path)

    if instructions:
        # Conteúdo injetado no contexto — dev não vê, Claude recebe
        print(instructions)

    sys.exit(0)


if __name__ == "__main__":
    main()
