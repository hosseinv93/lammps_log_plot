# LAMMPS Log Plotter

A small command-line tool to parse LAMMPS `log.lammps` files, handle multiple thermo runs, and plot or average selected columns.

Script file name (example): `lammps_log_plot.py`
Command name (if added to `$PATH`): `lammps-log-plot`

---

## Features

* Automatically detects **thermo blocks** in LAMMPS log files (each `run` / `minimize`).
* Supports **multiple runs** in a single log file.
* Lists runs with number of rows and available thermo columns.
* Plots one or more columns vs a chosen x-axis (typically `Step`).
* Restricts plotting and averaging to a given x-range (`--x-min`, `--x-max`).
* Computes averages of selected columns over the chosen x-range (`--avg-cols`).

---

## Requirements

* Python ≥ 3.8
* [`pandas`](https://pandas.pydata.org/)
* [`matplotlib`](https://matplotlib.org/)

Install with:

```bash
pip install pandas matplotlib
```

---

## Installation

### Clone / copy

```bash
git clone [https://github.com/<your-username>/<your-repo>.git](https://github.com/hosseinv93/lammps_log_plot.git)
cd lammps_log_plot
```

Make sure the script is named, e.g.:

```text
lammps_log_plot.py
```

### Make executable (optional)

```bash
chmod +x lammps_log_plot.py
```

Run locally with:

```bash
python lammps_log_plot.py log.lammps [options]
# or
./lammps_log_plot.py log.lammps [options]
```

### Optional: install as a command

```bash
cp lammps_log_plot.py ~/bin/lammps-log-plot
chmod +x ~/bin/lammps-log-plot
```

Add `~/bin` to your `PATH` in `~/.bashrc` if needed:

```bash
export PATH="$HOME/bin:$PATH"
source ~/.bashrc
```

Then you can use:

```bash
lammps-log-plot log.lammps [options]
```

---

## Usage

Show help:

```bash
lammps-log-plot -h
```

### 1. List runs and columns

```bash
lammps-log-plot log.lammps --list
```

Example output:

```text
Found 2 thermo run(s) in log.lammps:

Run 1: 2 rows, columns:
  Step  Temp  PotEng  Press  Volume

Run 2: 59 rows, columns:
  Step  Temp  PotEng  Press  Volume
```

### 2. Plot a single column vs `Step`

Temperature vs `Step` from run 2:

```bash
lammps-log-plot log.lammps --run 2 --x Step --y Temp
```

### 3. Plot multiple columns vs `Step`

```bash
lammps-log-plot log.lammps --run 1 --x Step --y Temp Press PotEng
```

### 4. Average columns over a timestep range

Average `Temp` and `Press` between `Step = 10000` and `20000` in run 2:

```bash
lammps-log-plot log.lammps \
    --run 2 --x Step \
    --avg-cols Temp Press \
    --x-min 10000 --x-max 20000
```

### 5. Plot and average at the same time

```bash
lammps-log-plot log.lammps \
    --run 2 --x Step \
    --y Temp \
    --avg-cols Temp \
    --x-min 100000 --x-max 200000
```

---

## Command-line options

```text
positional arguments:
  logfile         Path to LAMMPS log file (e.g., log.lammps)

optional arguments:
  -h, --help      Show this help message and exit
  --run RUN       Index of the run to use (1-based, default: 1)
  --x X           Column to use as x-axis / filter (default: Step)
  --y Y [Y ...]   One or more column names to plot vs x
  --list          List detected runs and their columns. If used
                  without --y or --avg-cols, exits after listing.
  --x-min X_MIN   Minimum x value (e.g. Step) to include
  --x-max X_MAX   Maximum x value (e.g. Step) to include
  --avg-cols COL [COL ...]
                  One or more column names to average over the
                  selected x-range
```

---
