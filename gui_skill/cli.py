import json
import shutil
import typer
import requests
from pathlib import Path
from rich.console import Console
from rich.table import Table

GITHUB_REPO = "galvesb/skills"
GITHUB_BRANCH = "main"
API_BASE = f"https://api.github.com/repos/{GITHUB_REPO}/contents"
RAW_BASE = f"https://raw.githubusercontent.com/{GITHUB_REPO}/{GITHUB_BRANCH}"

IGNORE_DIRS = {".github", "gui_skill", "__pycache__", ".git"}

app = typer.Typer(help="Gerenciador de skills para Claude Code", add_completion=False)
console = Console()


def _get_categories() -> list[str]:
    resp = requests.get(API_BASE, timeout=10)
    resp.raise_for_status()
    return [
        item["name"]
        for item in resp.json()
        if item["type"] == "dir" and item["name"] not in IGNORE_DIRS
    ]


def _get_skills(category: str) -> list[str]:
    resp = requests.get(f"{API_BASE}/{category}", timeout=10)
    resp.raise_for_status()
    return [
        item["name"]
        for item in resp.json()
        if item["type"] == "file" and item["name"].endswith(".md")
    ]


def _download_skill(category: str, filename: str) -> str:
    url = f"{RAW_BASE}/{category}/{filename}"
    resp = requests.get(url, timeout=10)
    resp.raise_for_status()
    return resp.text


def _install_hook(claude_dir: Path) -> None:
    """Copia o hook script e registra em settings.local.json."""
    hook_src = Path(__file__).parent / "hook.py"
    hook_dst = claude_dir / "skills_hook.py"
    shutil.copy2(hook_src, hook_dst)

    settings_path = claude_dir / "settings.local.json"
    settings = {}
    if settings_path.exists():
        try:
            settings = json.loads(settings_path.read_text())
        except Exception:
            settings = {}

    hook_command = f"python {hook_dst.absolute()}"

    hooks = settings.setdefault("hooks", {})
    user_prompt_hooks = hooks.setdefault("UserPromptSubmit", [])

    # Evita duplicar se já estiver configurado
    for entry in user_prompt_hooks:
        for h in entry.get("hooks", []):
            if h.get("command") == hook_command:
                return

    user_prompt_hooks.append({
        "hooks": [{"type": "command", "command": hook_command}]
    })

    settings_path.write_text(json.dumps(settings, indent=2, ensure_ascii=False))


@app.command()
def install(
    category: str = typer.Argument(..., help="Categoria de skills para instalar (ex: dev)"),
):
    """Instala skills de uma categoria no projeto atual."""
    claude_dir = Path(".claude")
    dest = claude_dir / "commands"
    dest.mkdir(parents=True, exist_ok=True)

    console.print(f"\n[bold]Buscando skills de '[cyan]{category}[/cyan]'...[/bold]")

    try:
        skills = _get_skills(category)
    except requests.HTTPError as e:
        if e.response.status_code == 404:
            console.print(f"[red]Categoria '{category}' não encontrada.[/red]")
            try:
                categories = _get_categories()
                console.print(f"[yellow]Disponíveis:[/yellow] {', '.join(categories)}")
            except Exception:
                pass
        else:
            console.print(f"[red]Erro: {e}[/red]")
        raise typer.Exit(1)

    if not skills:
        console.print(f"[yellow]Nenhuma skill encontrada em '{category}'.[/yellow]")
        raise typer.Exit(0)

    installed = []
    for skill in skills:
        try:
            content = _download_skill(category, skill)
            path = dest / skill
            already_exists = path.exists()
            path.write_text(content, encoding="utf-8")
            status = "[yellow]atualizado[/yellow]" if already_exists else "[green]instalado[/green]"
            console.print(f"  ✓ {skill} {status}")
            installed.append(skill)
        except Exception as e:
            console.print(f"  [red]✗ {skill} — {e}[/red]")

    # Instala o hook
    try:
        _install_hook(claude_dir)
        console.print(f"  ✓ hook [green]configurado[/green]")
    except Exception as e:
        console.print(f"  [yellow]⚠ hook não instalado: {e}[/yellow]")

    console.print(
        f"\n[bold green]{len(installed)} skill(s) instalada(s)[/bold green] "
        f"em [dim]{dest}/[/dim]\n"
    )

    console.print("[bold yellow]Variáveis de ambiente necessárias:[/bold yellow]")
    console.print("  export SKILLS_GITHUB_TOKEN=<seu_token_github>")
    console.print("  export SKILLS_PRIVATE_REPO=<owner/repo-privado>\n")


@app.command("list")
def list_categories():
    """Lista as categorias de skills disponíveis."""
    console.print("\n[bold]Buscando categorias...[/bold]")

    try:
        categories = _get_categories()
    except Exception as e:
        console.print(f"[red]Erro: {e}[/red]")
        raise typer.Exit(1)

    table = Table(show_header=False, box=None, padding=(0, 2))
    for cat in categories:
        table.add_row(f"[cyan]•[/cyan]", cat)

    console.print("\n[bold]Categorias disponíveis:[/bold]")
    console.print(table)
    console.print(f"\n[dim]Use: gui-skill install <categoria>[/dim]\n")


if __name__ == "__main__":
    app()
