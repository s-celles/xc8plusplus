"""
CLI interface for xc8plusplus transpiler using Typer.
"""

from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

from .transpiler import XC8Transpiler, transpile_directory

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
                console.print("\n[bold]Analysis Results:[/bold]")
                console.print(f"  Classes found: {len(transpiler.classes)}")
                for class_name, info in transpiler.classes.items():
                    console.print(
                        f"    • {class_name}: {len(info['methods'])} methods, {len(info['fields'])} fields"
                    )
                
                if transpiler.overloaded_functions:
                    console.print(f"  Overloaded functions found: {len(transpiler.overloaded_functions)}")
                    for func_name, overloads in transpiler.overloaded_functions.items():
                        console.print(f"    • {func_name}: {len(overloads)} overloads")
                        for overload in overloads:
                            console.print(f"      - {overload['mangled_name']}")
                
                if transpiler.main_function:
                    console.print("  Main function: Found and transpiled")
                else:
                    console.print("  Main function: Not found")
        else:
            console.print("[bold red]❌ Error:[/bold red] Transpilation failed")
            raise typer.Exit(1)

    except Exception as e:
        console.print(f"[bold red]❌ Error:[/bold red] {e}")
        raise typer.Exit(1) from e


@app.command()
def batch(
    source_dir: Path = typer.Argument(
        ...,
        help="Source directory containing C++ files",
        exists=True,
        file_okay=False,
        dir_okay=True,
        readable=True,
    ),
    output_dir: Optional[Path] = typer.Option(
        None,
        "--output",
        "-o",
        help="Output directory (default: source_dir/generated_c)",
    ),
    base_name: str = typer.Option(
        "transpiled_project",
        "--name",
        "-n",
        help="Base name for output files",
    ),
    stubs: bool = typer.Option(
        True,
        "--stubs/--no-stubs",
        help="Enable/disable XC8 macro stubs for better analysis",
    ),
    verbose: bool = typer.Option(
        False,
        "--verbose",
        "-v",
        help="Enable verbose output",
    ),
) -> None:
    """
    Transpile all C++ files in a directory to C code.

    This command finds all .cpp and .hpp files in the source directory and
    transpiles them to a single C output file. It also copies any existing
    .c and .h files to the output directory.
    """
    
    # Set default output directory if not provided
    if output_dir is None:
        output_dir = source_dir / "generated_c"

    if verbose:
        console.print(f"[bold blue]Source Directory:[/bold blue] {source_dir}")
        console.print(f"[bold blue]Output Directory:[/bold blue] {output_dir}")
        console.print(f"[bold blue]Base Name:[/bold blue] {base_name}")
        console.print(f"[bold blue]XC8 Stubs:[/bold blue] {'Enabled' if stubs else 'Disabled'}")

    # Find C++ files
    cpp_files = list(source_dir.glob("*.cpp")) + list(source_dir.glob("*.hpp"))
    
    if not cpp_files:
        console.print(f"[bold yellow]Warning:[/bold yellow] No C++ files found in {source_dir}")
        raise typer.Exit(0)

    console.print(f"[bold]Found {len(cpp_files)} C++ files:[/bold]")
    for cpp_file in cpp_files:
        console.print(f"  • {cpp_file.name}")

    try:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
            transient=True,
        ) as progress:
            task = progress.add_task("Analyzing and transpiling files...", total=None)

            # Create transpiler and configure XC8 stubs
            transpiler = XC8Transpiler()
            transpiler.xc8_stubs_enabled = stubs
            
            # Transpile all files
            success = transpiler.transpile_multiple_files(cpp_files, output_dir, base_name)

            progress.remove_task(task)

        if success:
            # Copy supporting files
            copied_files = transpiler.copy_supporting_files(source_dir, output_dir)
            
            console.print(
                f"[bold green]✅ Success![/bold green] Transpiled {len(cpp_files)} files → {output_dir}"
            )

            if verbose or True:  # Always show summary for batch operations
                summary = transpiler.get_analysis_summary()
                console.print("\n[bold]Transpilation Summary:[/bold]")
                console.print(f"  Input files analyzed: {summary['source_files']}")
                console.print(f"  Classes found: {summary['classes']}")
                console.print(f"  Overloaded functions: {summary['overloaded_functions']}")
                console.print(f"  Supporting files copied: {len(copied_files)}")
                console.print(f"  XC8 stubs: {'Enabled' if summary['xc8_stubs_enabled'] else 'Disabled'}")
                console.print(f"  Main function: {'Found' if summary['has_main'] else 'Not found'}")
                
                if verbose and transpiler.classes:
                    console.print("\n[bold]Classes Details:[/bold]")
                    for class_name, info in transpiler.classes.items():
                        console.print(
                            f"  • {class_name}: {len(info['methods'])} methods, {len(info['fields'])} fields"
                        )
                
                if verbose and transpiler.overloaded_functions:
                    console.print("\n[bold]Overloaded Functions:[/bold]")
                    for func_name, overloads in transpiler.overloaded_functions.items():
                        console.print(f"  • {func_name}: {len(overloads)} overloads")
                        for overload in overloads:
                            console.print(f"    - {overload['mangled_name']}")

            console.print(f"\n[bold]Next steps:[/bold]")
            console.print(f"  1. Review generated C code in: {output_dir}")
            console.print(f"  2. Implement any missing function bodies")
            console.print(f"  3. Test compilation with XC8")
        else:
            console.print("[bold red]❌ Error:[/bold red] Batch transpilation failed")
            raise typer.Exit(1)

    except Exception as e:
        console.print(f"[bold red]❌ Error:[/bold red] {e}")
        raise typer.Exit(1) from e
    finally:
        # Cleanup temporary files
        if 'transpiler' in locals():
            transpiler.cleanup_temp_files()


@app.command()
def version() -> None:
    """Show version information."""
    from . import __author__, __version__

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

    console.print("\n[bold]Example Usage:[/bold]")
    console.print("  xc8plusplus transpile input.cpp output.c")
    console.print("  xc8-cc -mcpu=16F18877 output.c -o firmware.hex")


def main() -> None:
    """Main entry point for the CLI."""
    app()


if __name__ == "__main__":
    main()
