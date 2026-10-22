# Dual-Feedback Starvation-Debt Scheduler (SDRR)

A discrete-event simulator comparing FCFS, SJF, Priority, Round Robin, and the Starvation-Debt Round Robin (SDRR) CPU scheduling algorithms.

## Setup (Windows — VS Code)

Open the project folder in VS Code and open the PowerShell terminal.

### 1. Create a virtual environment

```powershell
py -m venv .venv
```

### 2. Install dependencies

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

### 3. Run the project

Run the following commands in the VS Code PowerShell terminal.

**Textbook workload**
```powershell
.\.venv\Scripts\python.exe demo.py --workload textbook
```

**Mixed workload**
```powershell
.\.venv\Scripts\python.exe demo.py --workload mixed --seed 1
```

**Starvation-prone workload**
```powershell
.\.venv\Scripts\python.exe demo.py --workload starvation --seed 1
```

**Run experiments (200 trials)**
```powershell
.\.venv\Scripts\python.exe experiments.py --runs 200
```

**Run tests**
```powershell
.\.venv\Scripts\python.exe -m pytest -q
```

## Results

Charts and CSV files are written to the `results/` folder.

## Technologies Used

- Python
- Discrete-event simulation
- CPU scheduling algorithms
- Automated testing with pytest

## Team
Girisa P (24BCB0009), Thoshiyni S K (24BCB0146), Charishma M (24BCB0100), Pavithra R M (24BCI0050)
