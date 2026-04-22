import time
import functools
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn, TimeElapsedColumn
from rich.panel import Panel
from rich.text import Text
from rich import box
from rich.table import Table
 
console = Console()
 
def log_step(label: str, color: str = "cyan"):
    """
    Dekorator wyświetlający nazwę kroku, czas wykonania
    oraz kolorowy status powodzenia lub błędu.
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            console.print(f"\n[bold {color}]▶  {label}[/bold {color}]")
            start = time.perf_counter()
            try:
                result = func(*args, **kwargs)
                elapsed = time.perf_counter() - start
                console.print(f"[bold green]  ✓ Zakończono[/bold green] [dim]({elapsed:.1f}s)[/dim]")
                return result
            except Exception as e:
                elapsed = time.perf_counter() - start
                console.print(f"[bold red]  ✗ Błąd[/bold red] [dim]({elapsed:.1f}s)[/dim]: {e}")
                raise
        return wrapper
    return decorator
 
def with_progress_bar(label: str, color: str = "magenta"):
    """
    Dekorator dodający pasek postępu Rich do funkcji,
    która przetwarza fragmenty jeden po drugim.
    Funkcja opakowywana otrzymuje dodatkowy argument:
        progress_callback(current, total, fragment_label)
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            results = {}
 
            with Progress(
                SpinnerColumn(style=f"bold {color}"),
                TextColumn(f"[bold {color}]{label}[/bold {color}]"),
                BarColumn(bar_width=30, style=color, complete_style=f"bold {color}"),
                TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
                TextColumn("•"),
                TextColumn("[dim]{task.fields[fragment]}[/dim]"),
                TimeElapsedColumn(),
                console=console,
                transient=False,
            ) as progress:
                task = progress.add_task("", total=None, fragment="inicjalizacja...")
 
                def progress_callback(current: int, total: int, fragment_label: str = ""):
                    progress.update(task, total=total, completed=current, fragment=fragment_label)
 
                kwargs["progress_callback"] = progress_callback
                results = func(*args, **kwargs)
 
            return results
        return wrapper
    return decorator
 
def retry_with_status(max_retries: int = 5, initial_delay: int = 10):
    """
    Dekorator obsługujący retry z exponential backoff.
    Wyświetla kolorowe komunikaty o każdej próbie
    i odlicza czas do następnej.
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            delay = initial_delay
            for attempt in range(1, max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    error_str = str(e)
                    is_retryable = any(
                        code in error_str
                        for code in ["503", "429", "UNAVAILABLE", "RESOURCE_EXHAUSTED"]
                    )
                    if is_retryable and attempt < max_retries:
                        console.print(
                            f"  [bold yellow]⚠  API przeciążone[/bold yellow] "
                            f"[dim](próba {attempt}/{max_retries})[/dim] — "
                            f"czekam [bold]{delay}s[/bold]..."
                        )

                        for remaining in range(delay, 0, -1):
                            console.print(
                                f"    [dim]Ponowna próba za {remaining}s...[/dim]",
                                end="\r"
                            )
                            time.sleep(1)
                        console.print(" " * 40, end="\r")
                        delay *= 2
                    else:
                        raise
        return wrapper
    return decorator
 
def print_summary(records: list, output_path: str):
    """Wyświetla podsumowanie wyników w estetycznej tabeli."""
 
    table = Table(
        title="Wyniki transkrypcji",
        box=box.ROUNDED,
        border_style="cyan",
        header_style="bold magenta",
        show_lines=True,
    )
    table.add_column("Nr.", style="dim", width=5)
    table.add_column("Nr. posit.", style="bold white", width=12)
    table.add_column("Nomen", style="green", width=20)
    table.add_column("Data urodzenia", style="yellow", width=18)
    table.add_column("Ojciec", style="cyan", width=30)
 
    for i, rec in enumerate(records, 1):
        nr_posit = _safe_get(rec, "Nr. posit.") or "—"
        nomen    = _safe_get(rec, "nomen") or "—"
        natus    = _safe_get(rec, "Natus") or "—"
        parentes = _safe_get(rec, "Nomen et conditio") or "—"
        if len(parentes) > 35:
            parentes = parentes[:32] + "..."
 
        table.add_row(str(i), nr_posit, nomen, natus, parentes)
 
    console.print()
    console.print(table)
    console.print(
        Panel(
            f"[bold green]✓ Zapisano {len(records)} rekordów[/bold green]\n"
            f"[dim]Plik: {output_path}[/dim]",
            box=box.ROUNDED,
            border_style="green",
        )
    )
 
def _safe_get(d, key):
    """Rekurencyjne szukanie klucza w zagnieżdżonym słowniku."""
    if not isinstance(d, dict):
        return None
    if key in d:
        val = d[key]
        return val if not isinstance(val, dict) else None
    for v in d.values():
        result = _safe_get(v, key)
        if result is not None:
            return result
    return None