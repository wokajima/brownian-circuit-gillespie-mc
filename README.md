# brownian-circuit-gillespie-mc

## abstract
This repository contains the Gillespie-based Monte Carlo simulation and statistical analysis.

#### Packages and versions
- `python==3.12.7`
- `numpy==1.26.4`
- `pandas==2.2.2`
- `tqdm==4.66.5`
- `matplotlib==3.9.2`

### directory
```
.
├── README.md
├── requirements.txt
├── analysis/
│   ├── analysis.ipynb
│   ├── figure.ipynb
│   ├── data-chain.csv
│   ├── data-cube.csv
│   ├── data-full_adder.csv
│   └── ...
├── mc_sim/
│   ├── src/
│   │   ├── config/
│   │   │   ├── __init__.py
│   │   │   ├── chain.py
│   │   │   ├── cube.py
│   │   │   ├── full_adder.py
│   │   │   └── ...
│   │   └── brownian.py
│   └── main.py
└── data/
    ├── chain/
    ├── cube/
    ├── full_adder/
    └── ...
```

## mc_sim
mc_sim is a Python module for numerical analysis.
Circuit information is stored as Python code within src/config/. The currently registered circuits are as follows:
- chain
- cube
- mixing
- xor
- full_adder
- precede_adder
- product_adder

To run the simulation, execute main.py.

```bash
$ python3 main.py --circuit chain --module 16 --gamma 10 --trials 400
```

#### arguments
- ```--circuit``` \
Specify the name of the circuit.

- ```--module``` \
Specify the number of circuit modules to connect in series as an integer.
Multiple values can be specified, and simulations can be run independently for each one.

- ```--gamma``` \
Specify the forward transition rate.
Multiple values can be specified.

- ```--trials``` \
Specify the number of trials. The default value when omitted is 100.

The data is output as CSV files, sorted by circuit within the data directory; ```data/<circuit_name>/```.

## analysis
The analysis section contains two Jupyter notebooks for processing analysis results and generating charts. It converts mc_sim results into CSV files and generates graphs.

### ```data-loader.ipynb```
Converts the results of mc_sim into a data list. This will not work if you have not uploaded the numerical analysis results. Please run mc_sim and prepare the analysis results.

The data CSV file follows the format below.

```csv
name,mod,rate,time,mean_stderr,trial,std
chain,1,0.001,927.9062663887581,101.34622733547992,100,1013.4622733547992
chain,1,0.002,494.6579422663378,24.401092049992176,400,488.0218409998435
...
```
#### Definition of columns
- name \
Name of circuit
- mod \
Number of circuit modules
- rate \
Forward transition rate
- time \
mean value of first passage time
- mean_stderr \
Standard error of mean value of first passage time
- trial \
Number of trials
- std \
Standard deviation of first passage time

This CSV file is stored directly under the analysis directory as data-***.csv.

### ```figure.ipynb``` 
Generate graphs from data-***.csv. Simply run it to obtain the graphs.

## Circuits
This section introduces the circuits and their properties located in mc_sim/src/config/.

- chain \
A circuit that realizes Brownian motion on a one-dimensional chain.

- cube \
A circuit composed entirely of single-layer parallel elements; the state graph forms an N-dimensional hypercube.

- mixing \
A circuit whose state graph is a binary tree. For simplicity, other state graphs are mixed in, so in ```data-loader.ipynb``` they are separated individually and exported as ```data-mixing-C.csv``` and ```data-mixing-NC.csv```.

- xor \
A circuit whose state graph is a one-dimensional chain with backward branches of length 1.

- full_adder, precede_adder, product_adder \
Circuits implementing adders with carry input. The multiple types correspond to differences in circuit construction.


## Data Generation and Analysis
1. Install the virtual environment and dependencies

```bash
$ pip install -r requirements.txt
```

2. mc_sim allows simulation parameters to be specified from the bash command line.
```bash
$ python3 main.py --circuit full_adder --module 8 16 --gamma 2.4 3.2 --trials 800
```

3. analysis \
Run ```analysis.ipynb``` to generate data-***.csv.

4. figure \
Run ```figure.ipynb``` to generate the plots.