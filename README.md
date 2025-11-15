# Audio Denoising (Wavelets)

Wavelet denoising removes noise while preserving important features by thresholding small wavelet coefficients (VisuShrink/Universal threshold per Donoho & Johnstone) and reconstructing the signal. This repo provides Python and MATLAB implementations with a simple CLI and demos.

Key libs: PyWavelets (`pywt`), NumPy, SoundFile, Matplotlib.

## Quick start (Windows, PowerShell)

1) Create and activate a virtual environment, then install deps:

```powershell
py -3 -m venv .venv
.\.venv\Scripts\python -m pip install --upgrade pip
.\.venv\Scripts\python -m pip install -r requirements.txt
```

2) Put your input file at the project root, e.g. `sample_audio.wav`.

3) Denoise with the CLI (writes to `outputs/`):

```powershell
.\.venv\Scripts\python denoise.py denoise sample_audio.wav outputs\sample_audio_denoised_cli.wav
```

4) Optional: run the demo that mixes noise, denoises, and saves plots (good to hear/see the difference):

```powershell
# increase --noise-level for a clearer before/after difference
.\.venv\Scripts\python audio_demo.py --noise-level 0.20
```

Outputs (WAV) are written to `outputs/` and plots to `outputs/waveforms.png` and `outputs/spectrograms.png`.

## Programmatic usage (Python)

```python
from denoise import AudioDeNoise
import os

inp = "sample_audio.wav"
os.makedirs("outputs", exist_ok=True)
out = os.path.join("outputs", "input_denoised.wav")

# Basic denoise
AudioDeNoise(inp).deNoise(out)

# Optional: generate a predicted noise file from a noise-only sample

noise_sample = "white_noise_test.wav"  # or your own noise-only recording
pred_out = os.path.join("outputs", "input_noise_output.wav")
AudioDeNoise(inp).generateNoiseProfileTo(noise_sample, pred_out)
```

CLI help:

```powershell
.\.venv\Scripts\python denoise.py -h
# subcommands:
#   denoise <input> <output>
#   noise-profile <noise_sample> <output>
```

## Files and outputs

- Inputs (root)
    - `sample_audio.wav` — your main audio to denoise
    - `white_noise_test.wav` — optional noise-only sample (you can generate one via `white_noise.py`)
- Python scripts
    - `audio_denoiser.py` — minimal example; writes WAVs to `outputs/`
    - `audio_demo.py` — mixes noise (configurable), denoises, and saves plots; writes to `outputs/`
    - `denoise.py` — library + CLI for denoise/noise-profile
    - `white_noise.py` — generates a short white-noise WAV (optional)
- Outputs (auto-created)
    - `outputs/` — all generated WAVs, including:
        - `sample_audio_noisy.wav` (demo noisy mix)
        - `sample_audio_denoised.wav` (demo denoised)
        - `input_denoised.wav` (example denoised from `audio_denoiser.py`)
        - `predicted_noise.wav` (demo predicted noise from a noise-only sample)
        - `sample_audio_denoised_wdenoise.wav`, `sample_audio_denoised_matlab.wav` (from MATLAB)
    - `outputs/waveforms.png`, `outputs/spectrograms.png` — demo visualizations

Known benign warning: PyWavelets may print “Level value of 2 is too high: all coefficients will experience boundary effects.” for very short blocks. This does not stop processing; you can reduce the level if desired.

## MATLAB usage

Open `matlab/main.m` and press Run, or from the MATLAB command window:

```matlab
cd 'A:\work\dsp_project\matlab'
main
```

What it does:
- Denoises `sample_audio.wav` in two ways:
    - Single-shot: `wdenoise` (writes `outputs/sample_audio_denoised_wdenoise.wav`)
    - Chunked: calls `deNoiseAudio.m` (writes `outputs/sample_audio_denoised_matlab.wav`)
- Optional: if `white_noise_test.wav` exists, `extractNoise.m` can produce `outputs/predicted_noise_matlab.wav`
- Plots time-domain and spectrogram views
- Interactive playback: press Enter to hear a short “before” (noisy) and “after” (denoised) preview

Configuration flags in `main.m`:
- `WAVELET_NAME` (default `'db4'`)
- `LEVEL` (default `2`)
- `ADD_SYNTH_NOISE` and `NOISE_LEVEL` — set to add noise for a clear before/after demonstration

## Tips

- To hear a bigger difference, use the demo with a higher `--noise-level` (e.g., 0.2–0.3), or denoise a truly noisy recording.
- In VS Code, select the `.venv` interpreter before running (Python: Select Interpreter).
- If you want all artifacts (wav, png) contained, they are under `outputs/`.

## License

See `LICENSE`.

