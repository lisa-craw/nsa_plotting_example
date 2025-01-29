## Wurst party
# ![](https://github.com/lisa-craw/nsa_plotting_example/blob/main/wurst_tanzen.gif)

### Processed data

# ![](https://github.com/lisa-craw/nsa_plotting_example/blob/main/plots/wurst_pressure.png)

# ![](https://github.com/lisa-craw/nsa_plotting_example/blob/main/plots/temp_curves_together.png)

### Reassurance data

# ![](https://github.com/lisa-craw/nsa_plotting_example/blob/main/plots/logger_voltage.png)

# ![](https://github.com/lisa-craw/nsa_plotting_example/blob/main/plots/wurst_voltage.png)


## Running these scripts

These scripts were written using python 3.10.12.
The best way to run them is to create a virtual environment in the root of the `nsa_plotting_example` repository like so:

```bashs
python -m pip install virtualenv
python -m venv .env
```

On Linux, activate the environment with 

```bash
source .env/bin/activate
```

Or on Windows:

```bash
.env/Scripts/activate
```

Then install the requirements.txt:
```bash
python -m pip install -r requirements.txt
```

Run `cryowurst_raw_data_process.py` to take raw data from the `/data/raw/` directory and decode it to a .csv file in the `/data/processed/` directory.

Run `cryowurst_data_allplots.py` to take processed data from the `/data/processed/` directory and produce plots, saved to the `/plots/` directory.