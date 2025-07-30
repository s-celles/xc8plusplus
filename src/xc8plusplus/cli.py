"""
CLI interface for xc8plusplus transpiler using Typer.
"""

from pathlib import Path
from typing import Optional, List

import typer
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table
from rich.panel import Panel

# Import from the new transpilers module structure
from .transpilers.unified_transpiler import (
    XC8Transpiler,
    get_native_version,
    check_llvm,
)

# Check for native transpiler availability
try:
    from .transpilers.native_backend import is_available as native_available

    NATIVE_AVAILABLE = native_available()
except ImportError:
    NATIVE_AVAILABLE = False

app = typer.Typer(
    name="xc8plusplus",
    help="C++ to C transpiler for Microchip XC8 compiler",
    add_completion=False,
)
console = Console()

# Create a subcommand group for transpile operations
transpile_app = typer.Typer(
    name="transpile",
    help="Transpile C++ code to C",
    add_completion=False,
)
app.add_typer(transpile_app, name="transpile")


@transpile_app.command("file")
def transpile_file(
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
    target_device: str = typer.Option(
        "PIC16F876A",
        "--target",
        "-t",
        help="Target PIC device",
    ),
    include_dirs: List[str] = typer.Option(
        [],
        "--include",
        "-I",
        help="Include directory (can be used multiple times)",
    ),
    defines: List[str] = typer.Option(
        [],
        "--define",
        "-D",
        help="Preprocessor define (can be used multiple times)",
    ),
    no_optimization: bool = typer.Option(
        False,
        "--no-optimization",
        help="Disable optimizations",
    ),
    no_pragmas: bool = typer.Option(
        False,
        "--no-pragmas",
        help="Disable XC8 pragma generation",
    ),
    backend: str = typer.Option(
        "native",
        "--backend",
        "-b",
        help="Transpiler backend to use: 'native' (LLVM LibTooling) or 'python' (Clang AST)",
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

    # Validate backend parameter
    if backend not in ["native", "python"]:
        console.print(f"[bold red]❌ Error:[/bold red] Invalid backend '{backend}'. Must be 'native' or 'python'.")
        raise typer.Exit(1)

    # Set default output file if not provided
    if output_file is None:
        output_file = input_file.with_suffix(".c")

    if verbose:
        console.print(f"[bold blue]Input:[/bold blue] {input_file}")
        console.print(f"[bold blue]Output:[/bold blue] {output_file}")
        console.print(f"[bold blue]Target Device:[/bold blue] {target_device}")
        console.print(
            f"[bold blue]Native Backend Available:[/bold blue] {'Yes' if NATIVE_AVAILABLE else 'No'}"
        )

    try:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
            transient=True,
        ) as progress:
            task = progress.add_task("Transpiling C++ to C...", total=None)

            # Create transpiler with configuration
            transpiler = XC8Transpiler(
                backend=backend,
                enable_optimization=not no_optimization,
                generate_xc8_pragmas=not no_pragmas,
                target_device=target_device,
                include_paths=include_dirs,
                defines=defines,
            )

            # Show backend info
            if verbose:
                backend_info = transpiler.get_backend_info()
                console.print(
                    f"[bold blue]Using:[/bold blue] {backend_info['description']}"
                )

            # Perform transpilation
            result = transpiler.transpile_file(str(input_file), str(output_file))

            progress.remove_task(task)

        if result.success:
            console.print(
                f"[bold green]✅ Success![/bold green] Transpiled {input_file} → {output_file}"
            )

            if verbose:
                backend_info = transpiler.get_backend_info()
                console.print(
                    f"\n[bold]Backend:[/bold] {backend_info['backend']} ({backend_info['version']})"
                )

                if result.warnings:
                    console.print(
                        f"\n[bold yellow]Warnings ({len(result.warnings)}):[/bold yellow]"
                    )
                    for warning in result.warnings:
                        console.print(f"  ⚠️  {warning}")

                if result.generated_header_code:
                    header_lines = len(result.generated_header_code.splitlines())
                    console.print(
                        f"\n[bold]Generated header:[/bold] {header_lines} lines"
                    )

                if result.generated_c_code:
                    c_lines = len(result.generated_c_code.splitlines())
                    console.print(f"[bold]Generated C code:[/bold] {c_lines} lines")
        else:
            console.print("[bold red]❌ Error:[/bold red] Transpilation failed")
            if result.error_message:
                console.print(f"[red]{result.error_message}[/red]")
            raise typer.Exit(1)

    except Exception as e:
        console.print(f"[bold red]❌ Error:[/bold red] {e}")
        raise typer.Exit(1) from e


@transpile_app.command("batch")
def transpile_batch(
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
    target_device: str = typer.Option(
        "PIC16F876A",
        "--target",
        "-t",
        help="Target PIC device",
    ),
    include_dirs: List[str] = typer.Option(
        [],
        "--include",
        "-I",
        help="Include directory (can be used multiple times)",
    ),
    defines: List[str] = typer.Option(
        [],
        "--define",
        "-D",
        help="Preprocessor define (can be used multiple times)",
    ),
    no_optimization: bool = typer.Option(
        False,
        "--no-optimization",
        help="Disable optimizations",
    ),
    no_pragmas: bool = typer.Option(
        False,
        "--no-pragmas",
        help="Disable XC8 pragma generation",
    ),
    backend: str = typer.Option(
        "native",
        "--backend",
        "-b",
        help="Transpiler backend to use: 'native' (LLVM LibTooling) or 'python' (Clang AST)",
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

    # Validate backend parameter
    if backend not in ["native", "python"]:
        console.print(f"[bold red]❌ Error:[/bold red] Invalid backend '{backend}'. Must be 'native' or 'python'.")
        raise typer.Exit(1)

    # Set default output directory if not provided
    if output_dir is None:
        output_dir = source_dir / "generated_c"

    if verbose:
        console.print(f"[bold blue]Source Directory:[/bold blue] {source_dir}")
        console.print(f"[bold blue]Output Directory:[/bold blue] {output_dir}")
        console.print(f"[bold blue]Base Name:[/bold blue] {base_name}")
        console.print(f"[bold blue]Target Device:[/bold blue] {target_device}")
        console.print(
            f"[bold blue]Native Backend Available:[/bold blue] {'Yes' if NATIVE_AVAILABLE else 'No'}"
        )

    # Find C++ files
    cpp_files = list(source_dir.glob("*.cpp")) + list(source_dir.glob("*.hpp"))

    if not cpp_files:
        console.print(
            f"[bold yellow]Warning:[/bold yellow] No C++ files found in {source_dir}"
        )
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

            # Create output directory
            output_dir.mkdir(parents=True, exist_ok=True)

            # Create transpiler with configuration
            transpiler = XC8Transpiler(
                backend=backend,
                enable_optimization=not no_optimization,
                generate_xc8_pragmas=not no_pragmas,
                target_device=target_device,
                include_paths=include_dirs,
                defines=defines,
            )

            # Show backend info
            if verbose:
                backend_info = transpiler.get_backend_info()
                console.print(
                    f"[bold blue]Using:[/bold blue] {backend_info['description']}"
                )

            # Transpile all files using batch method to avoid duplication
            results_dict = transpiler.transpile_batch(cpp_files, output_dir)
            
            # Convert results to list format for compatibility
            all_success = True
            results = []
            for cpp_file in cpp_files:
                result = results_dict[str(cpp_file)]
                results.append((cpp_file, result))
                if not result.success:
                    all_success = False

            progress.remove_task(task)

        # Copy supporting C and H files that are not generated
        _copy_supporting_files(source_dir, output_dir, cpp_files)

        if all_success:
            console.print(
                f"[bold green]Success![/bold green] Transpiled {len(cpp_files)} files -> {output_dir}"
            )

            if verbose:
                backend_info = transpiler.get_backend_info()
                console.print(
                    f"\n[bold]Backend:[/bold] {backend_info['backend']} ({backend_info['version']})"
                )

                total_warnings = sum(len(result.warnings) for _, result in results)
                if total_warnings > 0:
                    console.print(
                        f"\n[bold yellow]Total Warnings:[/bold yellow] {total_warnings}"
                    )

                console.print(f"\n[bold]Generated Files:[/bold]")
                for cpp_file, result in results:
                    status = "✅" if result.success else "❌"
                    console.print(f"  {status} {cpp_file.name} → {cpp_file.stem}.c")
        else:
            console.print("[bold red]❌ Error:[/bold red] Some transpilations failed")
            for cpp_file, result in results:
                if not result.success:
                    console.print(
                        f"[red]  ❌ {cpp_file.name}: {result.error_message}[/red]"
                    )
            raise typer.Exit(1)

    except Exception as e:
        console.print(f"[bold red]❌ Error:[/bold red] {e}")
        raise typer.Exit(1) from e


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


@app.command()
def info() -> None:
    """
    Show information about available transpilers.
    """
    console.print("[bold blue]🔧 XC8++ Transpiler Information[/bold blue]")
    console.print()

    # Show backend availability
    table = Table(title="Available Backends")
    table.add_column("Backend", style="cyan")
    table.add_column("Status", style="green")
    table.add_column("Description", style="white")
    table.add_column("Features", style="yellow")

    # Native C++ backend
    if NATIVE_AVAILABLE:
        try:
            from .transpilers.native_backend import get_version, check_llvm

            status = "✅ Available"
            version = get_version()
            llvm_status = "✅" if check_llvm() else "❌"
            features = f"LLVM LibTooling, Semantic AST, Type Safety {llvm_status}"
        except Exception:
            status = "❌ Error"
            features = "Failed to initialize"
    else:
        status = "❌ Not Available"
        features = "Build required (see docs)"

    table.add_row(
        "Native C++", status, "Professional LLVM LibTooling transpiler", features
    )

    # Python backend
    table.add_row(
        "Python",
        "✅ Available",
        "Python transpiler using Clang AST",
        "AST parsing, Basic transpilation",
    )

    console.print(table)
    console.print()

    # Usage examples
    console.print("[bold]💡 Usage Examples:[/bold]")
    console.print("  [cyan]xc8plusplus transpile input.cpp output.c[/cyan]")
    console.print("  [cyan]xc8plusplus batch ./src --target PIC18F4620[/cyan]")
    console.print("  [cyan]xc8plusplus --backend python transpile input.cpp[/cyan]")
    console.print()

    if NATIVE_AVAILABLE:
        try:
            from .transpilers.native_backend import check_llvm

            if check_llvm():
                console.print(
                    "[bold green]🎉 Recommended:[/bold green] Use native backend for best results!"
                )
            else:
                console.print(
                    "[bold yellow]⚠️  Warning:[/bold yellow] LLVM not fully functional"
                )
        except Exception:
            pass
    else:
        console.print("[bold yellow]💡 Build native backend:[/bold yellow]")
        console.print("  1. Install LLVM/Clang development libraries")
        console.print("  2. Run: .\\build-scripts\\build_native.ps1")
        console.print("  3. Reinstall: pip install -e .")


@app.command()
def check() -> None:
    """
    Check system requirements and transpiler availability.
    """
    console.print("[bold blue]🔍 XC8++ System Check[/bold blue]")
    console.print()

    # Check Python backend
    console.print("[bold]Python Backend:[/bold]")
    try:
        transpiler = XC8Transpiler(use_native=False)
        console.print("  ✅ Available")
    except Exception as e:
        console.print(f"  ❌ Error: {e}")

    console.print()

    # Check native backend
    console.print("[bold]Native C++ Backend:[/bold]")
    if NATIVE_AVAILABLE:
        try:
            from .transpilers.native_backend import check_llvm, get_version

            console.print(f"  ✅ Available (version {get_version()})")

            if check_llvm():
                console.print("  ✅ LLVM/Clang functional")
            else:
                console.print("  ⚠️  LLVM/Clang issues detected")

        except Exception as e:
            console.print(f"  ❌ Error: {e}")
    else:
        console.print("  ❌ Not available")
        console.print("  💡 Run build script to enable native backend")

    console.print()

    # Check example files
    console.print("[bold]Example Files:[/bold]")
    example_dir = Path("examples")
    if example_dir.exists():
        example_files = list(example_dir.glob("**/*.cpp"))
        console.print(f"  ✅ Found {len(example_files)} example files")

        # Show arduino-multi example specifically
        arduino_multi = example_dir / "arduino-multi"
        if arduino_multi.exists():
            arduino_files = list(arduino_multi.glob("*.cpp"))
            console.print(f"  ✅ Arduino-multi example: {len(arduino_files)} files")
        else:
            console.print("  ⚠️  Arduino-multi example not found")
    else:
        console.print("  ⚠️  Examples directory not found")

    console.print()

    # Overall status
    if NATIVE_AVAILABLE:
        console.print(
            "[bold green]🎉 System Status: Ready for professional transpilation![/bold green]"
        )
    else:
        console.print(
            "[bold yellow]⚠️  System Status: Basic transpilation available[/bold yellow]"
        )
        console.print("[italic]   Build native backend for full functionality[/italic]")


def _copy_supporting_files(source_dir: Path, output_dir: Path, cpp_files: List[Path]) -> None:
    """Copy supporting C and H files that are not generated from C++ transpilation."""
    import shutil
    
    # Get list of base names that will be generated from C++ files
    generated_names = {cpp_file.stem for cpp_file in cpp_files}
    
    # Find all C and H files in source directory
    c_files = list(source_dir.glob("*.c"))
    h_files = list(source_dir.glob("*.h"))
    
    supporting_files = []
    
    # Filter out files that would be generated by transpilation
    for c_file in c_files:
        if c_file.stem not in generated_names:
            supporting_files.append(c_file)
    
    for h_file in h_files:
        if h_file.stem not in generated_names:
            supporting_files.append(h_file)
    
    # Copy supporting files to output directory
    if supporting_files:
        console.print(f"\n[bold]Copying {len(supporting_files)} supporting files:[/bold]")
        for file in supporting_files:
            dest_file = output_dir / file.name
            shutil.copy2(file, dest_file)
            console.print(f"  • {file.name}")


def main() -> None:
    """Main entry point for the CLI."""
    app()


if __name__ == "__main__":
    main()
