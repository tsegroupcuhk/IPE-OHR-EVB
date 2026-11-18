# Unbiased A1 (R1) and A4 (R4) water–vacuum slab examples

Each example contains isoprene + OH and 1024 water molecules (SMW4/Fw).
The full EVB potential is integrated in NVT at 300 K with a 0.5 fs time
step. 

Use CUDA-enabled OpenMM and NumPy. Copy the selected case to a separate
run directory, enter that directory, and run:

    python run_evb.py

The drivers retain the historical A1 (2.5 ns) and A4 (0.5 ns) run
lengths. They use the supplied initial State, which also sets the
periodic box at restart.

| Case | Box in recorded segment (nm) | Example DCD interval (ps) |
| --- | --- | --- |
| A1 | 3.132 × 3.132 × 12.528 | 2400–2500 |
| A4 | 3.132 × 3.132 × 10.0 | 400–500 |

Each DCD has 101 frames at 1 ps intervals, retaining the original
coordinates and box records. Load each DCD with the corresponding
case's inits/m2.psf (5141 particles). Times are relative to the start of
the respective recorded NVT segment. 
