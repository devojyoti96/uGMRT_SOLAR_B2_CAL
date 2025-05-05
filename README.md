# uGMRT Band-2 Solar Observation Calibration Scripts  
**Observation Date:** 25 June 2022  
**Developers:** Devojyoti Kansabanik, Soham Dey, Surajit Mondal

---

## Overview

This repository contains calibration scripts for processing uGMRT Band-2 solar data from the 25 June 2022 observation. The workflow includes:

- Converting raw LTA data to UV-FITS
- Importing data into CASA
- Performing bandpass and attenuation calibration
- Correcting polarization leakage
- Applying calibration to the solar field
- Final flagging of solar data
- Preparing for self-calibration and imaging

---

## Prerequisites

- Access to the GMRT Online Archive: https://naps.ncra.tifr.res.in/goa/
- GMRT tools: `listscan`, `gvfits`
- CASA (tested with CASA 6 or CASA 5.6)

---

## Processing Steps

### 1. Download Raw Data

Obtain the LTA and LTB files from the GMRT Online Archive for project code `42_028`, observation date `25-Jun-2022`.

---

### 2. Convert LTA to UV-FITS

Run the GMRT tools:

```bash
listscan 42_028
gvfits 42_028
```

This produces a full-polarization UV-FITS file named `42_028_25jun2022.uvfits`.

---

### 3. Import into CASA

Open CASA and run:

```python
importuvfits(fitsfile='42_028_25jun2022.uvfits', vis='42_028_25jun2022.ms')
```

> ⚠️ The MS name `42_028_25jun2022.ms` is hardcoded in the scripts.

---

### 4. Basic Calibration and Flagging

Run the CASA script to perform:

- Bandpass calibration
- Attenuation correction
- Polarization leakage calibration

```bash
casa -c cal_and_flag.py
```

---

### 5. Split the Solar Field

Extract the solar observation field (field ID 4):

```python
split(vis='42_028_25jun2022.ms', field='4', outputvis='sun_field4.ms', datacolumn='corrected')
```

---

### 6. Apply Calibration to Solar Data

Apply the calibration solutions to the split solar field:

```bash
casa -c apply_solutions_sun.py
```

---

### 7. Flagging on Corrected Solar Data

Perform additional flagging on the corrected solar Measurement Set:

```bash
casa -c flagging_sun.py
```

---

### 8. Imaging and Self-Calibration

These steps are **manual** and should be performed interactively using CASA tasks such as `tclean`, `gaincal`, and `applycal`.

Refer to the notes and examples provided in the `imaging/` folder (if present).

---

## Notes

- The scripts assume the default uGMRT polarization and antenna setup for Band-2.
- For issues related to polarization leakage or aliasing near the solar limb, additional manual inspection is recommended.
- Script outputs and calibration tables are saved in the working directory.

---

## Citation

If you use this pipeline or scripts in your analysis, please cite the related publications and acknowledge the developers.

---

## Contact

For questions or issues, please contact:
- Devojyoti Kansabanik (devojyoti96@gmail.com), Soham Dey (sdey@ncra.tifr.res.in)

