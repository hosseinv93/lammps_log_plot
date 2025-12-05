#!/usr/bin/env python3
"""
lammps_log_plot.py

Parse a LAMMPS log file containing multiple runs and plot selected columns.
Optionally, average selected columns over a chosen x-range (typically Step).

Usage examples
--------------
1) List all detected runs and their columns:
    python plot.py log.lammps --list

2) Plot Temperature vs Step from the 2nd run:
    python plot.py log.lammps --run 2 --x Step --y Temp

3) Plot multiple y-columns vs Step from the 1st run:
    python plot.py log.lammps --run 1 --x Step --y Temp Press PotEng

4) Average Temp and Press between Step = 10000 and 20000 for run 2:
    python plot.py log.lammps --run 2 --x Step --avg-cols Temp Press --x-min 10000 --x-max 20000

5) Do both averaging and plotting over a restricted range:
    python plot.py log.lammps --run 2 --x Step --y Temp Press --avg-cols Temp Press --x-min 10000 --x-max 20000
"""

import argparse
from typing import List
import pandas as pd
import matplotlib.pyplot as plt


def parse_lammps_log(path: str) -> List[pd.DataFrame]:
    """
    Parse a LAMMPS log file and return a list of thermo DataFrames.
    Each DataFrame corresponds to a 'run' (or minimize) block.

    A thermo block is detected as:
      - a line starting with 'Step' (the header)
      - followed by lines that start with a numeric value (the data)
      - ends when a non-numeric first token is found, when the
        number of columns changes, or on a blank line.
    """
    runs: List[pd.DataFrame] = []

    with open(path, "r") as f:
        lines = f.readlines()

    i = 0
    n = len(lines)

    while i < n:
        line = lines[i].strip()

        # Detect the header line of a thermo block
        if line.startswith("Step"):
            headers = line.split()
            i += 1
            data = []

            while i < n:
                line = lines[i].strip()

                # End of block on empty line
                if not line:
                    break

                parts = line.split()

                # Attempt to see if first token is numeric (= data line)
                try:
                    float(parts[0])
                except ValueError:
                    # Non-numeric first token -> end of this thermo block
                    break

                # If the number of columns doesn't match the header, also stop
                if len(parts) != len(headers):
                    break

                # Convert all values to float
                row = [float(p) for p in parts]
                data.append(row)

                i += 1

            if data:
                df = pd.DataFrame(data, columns=headers)
                runs.append(df)
        else:
            i += 1

    return runs


def main():
    parser = argparse.ArgumentParser(
        description="Read a LAMMPS log file and plot/average selected columns from a chosen run."
    )
    parser.add_argument("logfile", help="Path to LAMMPS log file (e.g., log.lammps)")
    parser.add_argument(
        "--run",
        type=int,
        default=1,
        help="Index of the run to use (1-based, default: 1)",
    )
    parser.add_argument(
        "--x",
        default="Step",
        help="Name of the column for the x-axis / filtering (default: Step)",
    )
    parser.add_argument(
        "--y",
        nargs="+",
        help="One or more column names for the y-axis (e.g., Temp Press PotEng)",
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="List detected runs and their columns. If used without --y or --avg-cols, exit after listing.",
    )
    parser.add_argument(
        "--x-min",
        type=float,
        help="Minimum x-axis value (e.g., Step) to include for plotting/averaging.",
    )
    parser.add_argument(
        "--x-max",
        type=float,
        help="Maximum x-axis value (e.g., Step) to include for plotting/averaging.",
    )
    parser.add_argument(
        "--avg-cols",
        nargs="+",
        help="One or more column names to average over the selected x-range.",
    )

    args = parser.parse_args()

    runs = parse_lammps_log(args.logfile)

    if not runs:
        print("No thermo runs (Step headers) found in the log file.")
        return

    # List runs (but optionally continue to plotting/averaging)
    if args.list:
        print(f"Found {len(runs)} thermo run(s) in {args.logfile}:")
        for idx, df in enumerate(runs, start=1):
            print(
                f"\nRun {idx}: {len(df)} rows, columns:\n  "
                + "  ".join(df.columns.tolist())
            )
        # If user only wanted listing (no plotting or averaging), exit here
        if args.y is None and args.avg_cols is None:
            return

    # Check selected run index
    run_idx = args.run
    if run_idx < 1 or run_idx > len(runs):
        print(
            f"Requested run index {run_idx} is out of range. "
            f"File has {len(runs)} run(s)."
        )
        return

    df = runs[run_idx - 1]

    # Sanity: x-column must exist
    if args.x not in df.columns:
        print(f"x-axis column '{args.x}' not found in run {run_idx}.")
        print("Available columns:", ", ".join(df.columns))
        return

    # Filter by x-range (if requested)
    df_sel = df.copy()
    if args.x_min is not None:
        df_sel = df_sel[df_sel[args.x] >= args.x_min]
    if args.x_max is not None:
        df_sel = df_sel[df_sel[args.x] <= args.x_max]

    if df_sel.empty:
        print("No data left after applying x-range filters.")
        return

    # Make sure there is something to do
    if (args.y is None or len(args.y) == 0) and not args.avg_cols:
        print(
            "Nothing to do: provide at least one --y column for plotting "
            "or at least one --avg-cols column for averaging."
        )
        return

    # Check that requested y-columns exist
    if args.y:
        missing_y = [col for col in args.y if col not in df.columns]
        if missing_y:
            print(f"The following y-axis columns were not found in run {run_idx}:")
            print("  " + ", ".join(missing_y))
            print("Available columns:", ", ".join(df.columns))
            return

    # Averages over selected x-range
    if args.avg_cols:
        missing_avg = [col for col in args.avg_cols if col not in df.columns]
        if missing_avg:
            print("The following --avg-cols were not found in run {run_idx}:")
            print("  " + ", ".join(missing_avg))
            print("Available columns:", ", ".join(df.columns))
        else:
            print(
                f"Averages for run {run_idx} "
                f"over {args.x} in "
                f"[{args.x_min if args.x_min is not None else df_sel[args.x].min()}, "
                f"{args.x_max if args.x_max is not None else df_sel[args.x].max()}]:"
            )
            for col in args.avg_cols:
                mean_val = df_sel[col].mean()
                print(f"  {col}: {mean_val:.6g}")

    # Plot (if y-columns are given)
    if args.y:
        fig, ax = plt.subplots()
        x = df_sel[args.x]

        for col in args.y:
            ax.plot(x, df_sel[col], label=col)

        ax.set_xlabel(args.x)
        ax.set_ylabel(" / ".join(args.y))
        title = f"{args.logfile} – run {run_idx}"
        if args.x_min is not None or args.x_max is not None:
            title += f" (filtered {args.x})"
        ax.set_title(title)
        ax.legend()
        ax.grid(True)

        plt.tight_layout()
        plt.show()


if __name__ == "__main__":
    main()
