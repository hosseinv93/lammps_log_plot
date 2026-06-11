#!/usr/bin/env python3
"""
lammps_log_plot.py

Parse one or more LAMMPS log files containing multiple runs and plot selected columns.
Optionally average selected columns over a chosen x-range and save the plotted data.

Examples
--------
1) List all detected runs and columns in several logs:
    python plot.py log1.lammps log2.lammps --list

2) Plot Temperature vs Step from run 2 for several logs:
    python plot.py log1.lammps log2.lammps --run 2 --x Step --y Temp

3) Plot multiple y-columns vs Step:
    python plot.py log1.lammps log2.lammps --run 1 --x Step --y Temp Press PotEng

4) Average Temp and Press between Step 10000 and 20000:
    python plot.py log1.lammps log2.lammps --run 2 --x Step --avg-cols Temp Press --x-min 10000 --x-max 20000

5) Plot and save plotted data:
    python plot.py run1/log.lammps run2/log.lammps --run 1 --x Step --y Temp PotEng --save-data compare.dat

6) Save as CSV:
    python plot.py run1/log.lammps run2/log.lammps --run 1 --x Step --y Temp --save-data compare.csv --sep ,
"""

import argparse
import re
from pathlib import Path
from typing import List, Dict, Tuple

import pandas as pd
import matplotlib.pyplot as plt


def parse_lammps_log(path: str) -> List[pd.DataFrame]:
    """
    Parse a LAMMPS log file and return a list of thermo DataFrames.

    A thermo block is detected as:
      - a line starting with 'Step'
      - followed by numeric data lines
      - ends when a non-numeric first token is found, when the number
        of columns changes, or on a blank line.
    """
    runs: List[pd.DataFrame] = []

    with open(path, "r") as f:
        lines = f.readlines()

    i = 0
    n = len(lines)

    while i < n:
        line = lines[i].strip()

        if line.startswith("Step"):
            headers = line.split()
            i += 1
            data = []

            while i < n:
                line = lines[i].strip()

                if not line:
                    break

                parts = line.split()

                try:
                    float(parts[0])
                except ValueError:
                    break

                if len(parts) != len(headers):
                    break

                try:
                    row = [float(p) for p in parts]
                except ValueError:
                    break

                data.append(row)
                i += 1

            if data:
                df = pd.DataFrame(data, columns=headers)
                runs.append(df)
        else:
            i += 1

    return runs


def safe_label_from_path(path: str) -> str:
    """
    Create a readable label from the log path.

    Example:
        run1/log.lammps -> run1_log
        eps2/run3/log.lammps -> run3_log
    """
    p = Path(path)

    if p.parent.name:
        label = f"{p.parent.name}_{p.stem}"
    else:
        label = p.stem

    label = re.sub(r"[^A-Za-z0-9_]+", "_", label)
    label = re.sub(r"_+", "_", label)
    return label.strip("_")


def make_unique_labels(paths: List[str]) -> Dict[str, str]:
    """
    Make unique labels for each log file.
    """
    labels = {}
    used = {}

    for path in paths:
        base = safe_label_from_path(path)

        if base not in used:
            used[base] = 1
            labels[path] = base
        else:
            used[base] += 1
            labels[path] = f"{base}_{used[base]}"

    return labels


def select_x_range(
    df: pd.DataFrame,
    xcol: str,
    x_min: float | None,
    x_max: float | None,
) -> pd.DataFrame:
    """
    Filter DataFrame by x range.
    """
    df_sel = df.copy()

    if x_min is not None:
        df_sel = df_sel[df_sel[xcol] >= x_min]

    if x_max is not None:
        df_sel = df_sel[df_sel[xcol] <= x_max]

    return df_sel


def save_plotted_data(
    selected_data: List[Tuple[str, pd.DataFrame]],
    xcol: str,
    ycols: List[str],
    output_path: str,
    sep: str,
):
    """
    Save plotted data in wide format.

    The first column is xcol.
    Each following column is one selected y-column from one log file.

    Example columns:
        Step  run1_log_Temp  run2_log_Temp
    """
    merged = None

    for label, df in selected_data:
        cols = [xcol] + ycols
        out = df[cols].copy()

        rename_map = {col: f"{label}_{col}" for col in ycols}
        out = out.rename(columns=rename_map)

        if merged is None:
            merged = out
        else:
            merged = pd.merge(merged, out, on=xcol, how="outer")

    if merged is None:
        print("No data to save.")
        return

    merged = merged.sort_values(by=xcol)

    merged.to_csv(output_path, sep=sep, index=False)
    print(f"Saved plotted data to: {output_path}")


def main():
    parser = argparse.ArgumentParser(
        description="Read one or more LAMMPS log files and plot/average selected columns."
    )

    parser.add_argument(
        "logfiles",
        nargs="+",
        help="Path(s) to LAMMPS log file(s), e.g. log.lammps run2/log.lammps",
    )

    parser.add_argument(
        "--run",
        type=int,
        default=1,
        help="Index of the run to use from each log file, 1-based. Default: 1",
    )

    parser.add_argument(
        "--x",
        default="Step",
        help="Column for x-axis and filtering. Default: Step",
    )

    parser.add_argument(
        "--y",
        nargs="+",
        help="One or more columns for plotting, e.g. Temp Press PotEng",
    )

    parser.add_argument(
        "--list",
        action="store_true",
        help="List detected runs and columns for each log file.",
    )

    parser.add_argument(
        "--x-min",
        type=float,
        help="Minimum x value to include for plotting/averaging.",
    )

    parser.add_argument(
        "--x-max",
        type=float,
        help="Maximum x value to include for plotting/averaging.",
    )

    parser.add_argument(
        "--avg-cols",
        nargs="+",
        help="One or more columns to average over the selected x-range.",
    )

    parser.add_argument(
        "--save-data",
        help="Save the plotted data to this file, e.g. compare.dat or compare.csv.",
    )

    parser.add_argument(
        "--sep",
        default=" ",
        help="Separator for saved data. Use ',' for CSV. Default: space.",
    )

    parser.add_argument(
        "--save-fig",
        help="Save the figure to this file, e.g. plot.png or plot.pdf.",
    )

    parser.add_argument(
        "--no-show",
        action="store_true",
        help="Do not display the plot window. Useful when only saving the figure/data.",
    )

    args = parser.parse_args()

    all_runs: Dict[str, List[pd.DataFrame]] = {}

    for logfile in args.logfiles:
        runs = parse_lammps_log(logfile)
        all_runs[logfile] = runs

        if not runs:
            print(f"No thermo runs found in: {logfile}")

    labels = make_unique_labels(args.logfiles)

    if args.list:
        for logfile, runs in all_runs.items():
            print(f"\nFile: {logfile}")
            print(f"Found {len(runs)} thermo run(s).")

            for idx, df in enumerate(runs, start=1):
                print(
                    f"  Run {idx}: {len(df)} rows, columns:\n    "
                    + "  ".join(df.columns.tolist())
                )

        if args.y is None and args.avg_cols is None:
            return

    if (args.y is None or len(args.y) == 0) and not args.avg_cols:
        print(
            "Nothing to do: provide at least one --y column for plotting "
            "or at least one --avg-cols column for averaging."
        )
        return

    selected_data: List[Tuple[str, pd.DataFrame]] = []

    fig = None
    ax = None

    if args.y:
        fig, ax = plt.subplots()

    for logfile, runs in all_runs.items():
        if not runs:
            continue

        if args.run < 1 or args.run > len(runs):
            print(
                f"Skipping {logfile}: requested run {args.run}, "
                f"but file has only {len(runs)} run(s)."
            )
            continue

        df = runs[args.run - 1]
        label = labels[logfile]

        if args.x not in df.columns:
            print(f"Skipping {logfile}: x-column '{args.x}' not found.")
            print("Available columns:", ", ".join(df.columns))
            continue

        df_sel = select_x_range(df, args.x, args.x_min, args.x_max)

        if df_sel.empty:
            print(f"Skipping {logfile}: no data left after x-range filtering.")
            continue

        if args.y:
            missing_y = [col for col in args.y if col not in df.columns]
            if missing_y:
                print(f"Skipping plot for {logfile}: missing y-column(s):")
                print("  " + ", ".join(missing_y))
                print("Available columns:", ", ".join(df.columns))
            else:
                x = df_sel[args.x]

                for col in args.y:
                    ax.plot(x, df_sel[col], label=f"{label}: {col}")

                selected_data.append((label, df_sel))

        if args.avg_cols:
            missing_avg = [col for col in args.avg_cols if col not in df.columns]

            if missing_avg:
                print(f"Skipping averages for {logfile}: missing column(s):")
                print("  " + ", ".join(missing_avg))
                print("Available columns:", ", ".join(df.columns))
            else:
                xmin_used = args.x_min if args.x_min is not None else df_sel[args.x].min()
                xmax_used = args.x_max if args.x_max is not None else df_sel[args.x].max()

                print(
                    f"\nAverages for {logfile}, run {args.run}, "
                    f"over {args.x} in [{xmin_used}, {xmax_used}]:"
                )

                for col in args.avg_cols:
                    mean_val = df_sel[col].mean()
                    std_val = df_sel[col].std()
                    print(f"  {col}: mean = {mean_val:.6g}, std = {std_val:.6g}")

    if args.save_data:
        if not args.y:
            print("Cannot save plotted data because no --y columns were given.")
        elif not selected_data:
            print("No valid plotted data available to save.")
        else:
            save_plotted_data(
                selected_data=selected_data,
                xcol=args.x,
                ycols=args.y,
                output_path=args.save_data,
                sep=args.sep,
            )

    if args.y and ax is not None:
        ax.set_xlabel(args.x)
        ax.set_ylabel(" / ".join(args.y))

        title = f"Run {args.run}"
        if args.x_min is not None or args.x_max is not None:
            title += f" filtered by {args.x}"

        ax.set_title(title)
        ax.legend()
        ax.grid(True)

        plt.tight_layout()

        if args.save_fig:
            plt.savefig(args.save_fig, dpi=300)
            print(f"Saved figure to: {args.save_fig}")

        if not args.no_show:
            plt.show()


if __name__ == "__main__":
    main()
