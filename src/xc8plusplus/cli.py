"""
CLI interface for xc8plusplus transpiler using Typer.
"""

import typer
from pathlib import Path
from typing import Optional
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

from .transpiler import XC8Transpiler

app = typer.Typer(
    name="xc8plusplus",
    help="C++ to C transpiler for Microchip XC8 compiler",
    add_completion=False,
)
console = Console()


@app.command()
def transpile(
    input_file: Path = typer.Argument(
        ...,
        help="Input C++ file to transpile",
        exists=True,
        file_okay=True,
        dir_okay=False,
        readable=True,
    ),
    output_file: Optional[Path] = typer.Option(
        None,
        "--output",
        "-o",
        help="Output C file path (default: input_file with .c extension)",
    ),
    verbose: bool = typer.Option(
        False,
        "--verbose",
        "-v",
        help="Enable verbose output",
    ),
) -> None:
    """
    Transpile C++ code to C code compatible with XC8 compiler.

    This command takes a C++ source file and converts it to equivalent C code
    that can be compiled with Microchip's XC8 compiler for 8-bit PIC microcontrollers.
    """

    # Set default output file if not provided
    if output_file is None:
        output_file = input_file.with_suffix(".c")

    if verbose:
        console.print(f"[bold blue]Input:[/bold blue] {input_file}")
        console.print(f"[bold blue]Output:[/bold blue] {output_file}")

    try:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
            transient=True,
        ) as progress:
            task = progress.add_task("Transpiling C++ to C...", total=None)

            transpiler = XC8Transpiler()
            success = transpiler.transpile(str(input_file), str(output_file))

            progress.remove_task(task)

        if success:
            console.print(
                f"[bold green]✅ Success![/bold green] Transpiled {input_file} → {output_file}"
            )

            if verbose:
                console.print(f"\n[bold]Analysis Results:[/bold]")
                console.print(f"  Classes found: {len(transpiler.classes)}")
                for class_name, info in transpiler.classes.items():
                    console.print(
                        f"    • {class_name}: {len(info['methods'])} methods, {len(info['fields'])} fields"
                    )
        else:
            console.print("[bold red]❌ Error:[/bold red] Transpilation failed")
            raise typer.Exit(1)

    except Exception as e:
        console.print(f"[bold red]❌ Error:[/bold red] {e}")
        raise typer.Exit(1)


@app.command()
def version() -> None:
    """Show version information."""
    from . import __version__, __author__

    console.print(f"[bold]xc8plusplus[/bold] version {__version__}")
    console.print(f"Author: {__author__}")


@app.command()
def demo() -> None:
    """Show architecture demonstration."""
    console.print("[bold blue]xc8plusplus Architecture Demo[/bold blue]")
    console.print(
        "\nThis transpiler uses [bold]semantic AST analysis[/bold] instead of string manipulation:"
    )
    console.print("  • [green]Clang AST parsing[/green] - Compiler-grade C++ analysis")
    console.print(
        "  • [green]Semantic transformation[/green] - Understands C++ constructs"
    )
    console.print("  • [green]XC8 compatibility[/green] - Generates optimized C code")
    console.print(
        "  • [green]Memory efficient[/green] - Suitable for 8-bit microcontrollers"
    )

    console.print(f"\n[bold]Example Usage:[/bold]")
    console.print(f"  xc8plusplus transpile input.cpp output.c")
    console.print(f"  xc8-cc -mcpu=16F18877 output.c -o firmware.hex")


def main() -> None:
    """Main entry point for the CLI."""
    app()


if __name__ == "__main__":
    main()
