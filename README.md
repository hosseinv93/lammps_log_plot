# LAMMPS Log Plotter

A small command-line tool to parse LAMMPS `log.lammps` files, handle multiple thermo runs, and plot, average, or export selected thermo columns.

Script file name, for example:

```text
lammps_log_plot.py
```

Suggested command name if added to your `$PATH`:

```text
lammps-log-plot
```

---

## Features

- Automatically detects thermo blocks in LAMMPS log files.
- Supports multiple `run` or `minimize` thermo blocks in a single log file.
- Supports plotting the same selected columns from multiple log files.
- Lists detected runs with number of rows and available thermo columns.
- Plots one or more columns versus a chosen x-axis, usually `Step`.
- Restricts plotting and averaging to a chosen x-range using `--x-min` and `--x-max`.
- Computes averages and standard deviations of selected columns over the chosen x-range.
- Saves plotted data to a text or CSV file using `--save-data`.
- Saves figures directly to image/PDF files using `--save-fig`.
- Can run without opening a plot window using `--no-show`.

---

## Requirements

- Python 3.8 or newer
- [`pandas`](https://pandas.pydata.org/)
- [`matplotlib`](https://matplotlib.org/)

Install the required Python packages with:

```bash
pip install pandas matplotlib
```

or, if you use a system where `pip` points to Python 2:

```bash
python3 -m pip install pandas matplotlib
```

---

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/hosseinv93/lammps_log_plot.git
cd lammps_log_plot
```

Make sure the script is present, for example:

```text
lammps_log_plot.py
```

### 2. Make the script executable

```bash
chmod +x lammps_log_plot.py
```

You can then run it locally with:

```bash
python3 lammps_log_plot.py log.lammps [options]
```

or:

```bash
./lammps_log_plot.py log.lammps [options]
```

### 3. Optional: install as a terminal command

A convenient option is to install it in your local user binary directory:

```bash
mkdir -p ~/.local/bin
cp lammps_log_plot.py ~/.local/bin/lammps-log-plot
chmod +x ~/.local/bin/lammps-log-plot
```

Make sure `~/.local/bin` is in your `$PATH`. Add this line to `~/.bashrc` if needed:

```bash
export PATH="$HOME/.local/bin:$PATH"
```

Then reload your shell configuration:

```bash
source ~/.bashrc
```

Now you can run:

```bash
lammps-log-plot log.lammps [options]
```

Alternatively, for a system-wide installation:

```bash
sudo install -m 755 lammps_log_plot.py /usr/local/bin/lammps-log-plot
```

Then check that the command is available:

```bash
which lammps-log-plot
```

---

## Usage

Show help:

```bash
lammps-log-plot -h
```

General syntax:

```bash
lammps-log-plot LOGFILE [LOGFILE ...] [options]
```

For example:

```bash
lammps-log-plot log.lammps ../run2/log.lammps --run 3 --x Step --y Temp
```

---

## Examples

### 1. List detected runs and thermo columns

```bash
lammps-log-plot log.lammps --list
```

For multiple log files:

```bash
lammps-log-plot log.lammps ../2_pi2/log.lammps --list
```

Example output:

```text
File: log.lammps
Found 3 thermo run(s).
  Run 1: 101 rows, columns:
    Step  Temp  PotEng  Press  Volume
  Run 2: 501 rows, columns:
    Step  Temp  PotEng  Press  Volume
  Run 3: 1001 rows, columns:
    Step  Temp  PotEng  Press  Volume  f_chareg[3]
```

### 2. Plot a single column versus `Step`

```bash
lammps-log-plot log.lammps --run 2 --x Step --y Temp
```

### 3. Plot the same column from multiple log files

```bash
lammps-log-plot log.lammps ../2_pi2/log.lammps \
    --run 3 \
    --x Step \
    --y 'f_chareg[3]'
```

The quotes around `'f_chareg[3]'` are recommended because square brackets can be interpreted by the shell.

### 4. Plot multiple columns

```bash
lammps-log-plot log.lammps \
    --run 1 \
    --x Step \
    --y Temp Press PotEng
```

For multiple log files:

```bash
lammps-log-plot run1/log.lammps run2/log.lammps run3/log.lammps \
    --run 1 \
    --x Step \
    --y Temp PotEng
```

### 5. Average columns over a timestep range

Average `Temp` and `Press` between `Step = 10000` and `Step = 20000` in run 2:

```bash
lammps-log-plot log.lammps \
    --run 2 \
    --x Step \
    --avg-cols Temp Press \
    --x-min 10000 \
    --x-max 20000
```

### 6. Plot and average at the same time

```bash
lammps-log-plot log.lammps \
    --run 2 \
    --x Step \
    --y Temp \
    --avg-cols Temp \
    --x-min 100000 \
    --x-max 200000
```

### 7. Save plotted data to a file

Save plotted data from two logs into a space-separated text file:

```bash
lammps-log-plot log.lammps ../2_pi2/log.lammps \
    --run 3 \
    --x Step \
    --y 'f_chareg[3]' \
    --save-data charge_compare.dat
```

The output file will contain a wide table, for example:

```text
Step log_f_chareg[3] 2_pi2_log_f_chareg[3]
0    0.00123          0.00145
1000 0.00127          0.00149
2000 0.00130          0.00151
```

### 8. Save plotted data as CSV

```bash
lammps-log-plot log.lammps ../2_pi2/log.lammps \
    --run 3 \
    --x Step \
    --y 'f_chareg[3]' \
    --save-data charge_compare.csv \
    --sep ,
```

### 9. Save the figure

```bash
lammps-log-plot log.lammps ../2_pi2/log.lammps \
    --run 3 \
    --x Step \
    --y 'f_chareg[3]' \
    --save-fig charge_compare.png
```

For a PDF figure:

```bash
lammps-log-plot log.lammps ../2_pi2/log.lammps \
    --run 3 \
    --x Step \
    --y 'f_chareg[3]' \
    --save-fig charge_compare.pdf
```

### 10. Save data and figure without opening a plot window

This is useful on clusters or remote machines without a graphical display:

```bash
lammps-log-plot log.lammps ../2_pi2/log.lammps \
    --run 3 \
    --x Step \
    --y 'f_chareg[3]' \
    --save-data charge_compare.dat \
    --save-fig charge_compare.png \
    --no-show
```

---

## Command-line options

```text
positional arguments:
  logfiles              One or more LAMMPS log files.

optional arguments:
  -h, --help            Show help message and exit.

  --run RUN             Index of the thermo run to use from each log file.
                        The index is 1-based. Default: 1.

  --x X                 Column to use as the x-axis and for filtering.
                        Default: Step.

  --y Y [Y ...]         One or more column names to plot versus the x column.

  --list                List detected runs and their columns.
                        If used without --y or --avg-cols, the program exits
                        after listing.

  --x-min X_MIN         Minimum x value to include for plotting or averaging.

  --x-max X_MAX         Maximum x value to include for plotting or averaging.

  --avg-cols COL [COL ...]
                        One or more column names to average over the selected
                        x-range.

  --save-data FILE      Save the plotted data to a text or CSV file.

  --sep SEP             Separator for saved data.
                        Default: space.
                        Use --sep , for CSV output.

  --save-fig FILE       Save the plot to a file, for example plot.png,
                        plot.pdf, or plot.svg.

  --no-show             Do not open the plot window.
                        Useful when saving figures on a remote machine.
```

---

## Notes

### Column names with special characters

Some LAMMPS thermo column names contain square brackets, for example:

```text
f_chareg[3]
```

When using such columns in the terminal, quote them:

```bash
lammps-log-plot log.lammps --x Step --y 'f_chareg[3]'
```

### Multiple log files

When multiple log files are given, the same `--run`, `--x`, and `--y` selections are applied to each file.

Example:

```bash
lammps-log-plot log.lammps ../2_pi2/log.lammps \
    --run 3 \
    --x Step \
    --y 'f_chareg[3]'
```

### Different timesteps in different logs

When saving data from multiple logs, the script merges data using the selected x-column. If the logs have different timestep values, missing entries are left empty in the saved file.

### Running on remote machines

If you are working on a cluster or remote machine without graphical display, use:

```bash
lammps-log-plot log.lammps \
    --x Step \
    --y Temp \
    --save-fig temp.png \
    --no-show
```

---

## License

Choose a license that fits your needs. For example, you can add an MIT License file if you want the code to be openly reusable.

---

## Author

Hossein Vahid Dastjerdi
