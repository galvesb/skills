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


@app.command()
def install(
    category: str = typer.Argument(..., help="Categoria de skills para instalar (ex: dev)"),
):
    """Instala skills de uma categoria no projeto atual."""
    dest = Path(".claude/commands")
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
            console.print(f"[red]Erro ao buscar categoria: {e}[/red]")
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

    console.print(
        f"\n[bold green]{len(installed)} skill(s) instalada(s)[/bold green] "
        f"em [dim]{dest}/[/dim]\n"
    )


@app.command("list")
def list_categories():
    """Lista as categorias de skills disponíveis."""
    console.print("\n[bold]Buscando categorias...[/bold]")

    try:
        categories = _get_categories()
    except Exception as e:
        console.print(f"[red]Erro ao buscar categorias: {e}[/red]")
        raise typer.Exit(1)

    table = Table(show_header=False, box=None, padding=(0, 2))
    for cat in categories:
        table.add_row(f"[cyan]•[/cyan]", cat)

    console.print("\n[bold]Categorias disponíveis:[/bold]")
    console.print(table)
    console.print(f"\n[dim]Use: gui-skill install <categoria>[/dim]\n")


if __name__ == "__main__":
    app()
