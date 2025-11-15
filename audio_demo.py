import os
import argparse
import numpy as np
import soundfile as sf
import matplotlib.pyplot as plt

from denoise import AudioDeNoise


def read_mono(path):
    data, sr = sf.read(path)
    # if stereo, take first channel
    if data.ndim > 1:
        data = data[:, 0]
    return data, sr


def mix_noise(clean, noise, noise_level=0.05):
    # ensure noise length >= clean length
    if len(noise) < len(clean):
        repeats = int(np.ceil(len(clean) / len(noise)))
        noise = np.tile(noise, repeats)[: len(clean)]
    else:
        noise = noise[: len(clean)]

    noisy = clean + noise * noise_level
    # normalize to avoid clipping
    peak = np.max(np.abs(noisy))
    if peak > 1.0:
        noisy = noisy / peak
    return noisy


def plot_waveforms(signals: dict, sr: int, out_png: str):
    # signals: name -> numpy array
    plt.figure(figsize=(14, 8))
    n = len(signals)
    for i, (name, sig) in enumerate(signals.items(), start=1):
        t = np.arange(len(sig)) / sr
        ax = plt.subplot(n, 1, i)
        ax.plot(t, sig, linewidth=0.6)
        ax.set_xlim(0, t[-1])
        ax.set_ylabel(name)
        if i == n:
            ax.set_xlabel('Time (s)')
    plt.tight_layout()
    plt.savefig(out_png)
    plt.close()


def plot_spectrograms(signals: dict, sr: int, out_png: str):
    plt.figure(figsize=(14, 8))
    n = len(signals)
    for i, (name, sig) in enumerate(signals.items(), start=1):
        ax = plt.subplot(n, 1, i)
        Pxx, freqs, bins, im = ax.specgram(sig, NFFT=1024, Fs=sr, noverlap=512, cmap='magma')
        ax.set_ylabel(name)
        if i == n:
            ax.set_xlabel('Time (s)')
    plt.tight_layout()
    plt.savefig(out_png)
    plt.close()


def main():
    parser = argparse.ArgumentParser(description='Audio demo: mix noise, denoise, and visualize')
    parser.add_argument('--noise-level', type=float, default=0.05, help='Scaling for added noise when creating the noisy file (default: 0.05)')
    parser.add_argument('--clean', default='sample_audio.wav', help='Path to clean (or already noisy) input audio')
    parser.add_argument('--noise', default='white_noise_test.wav', help='Path to noise sample (used if present)')
    parser.add_argument('--out-dir', default='outputs', help='Directory to write outputs (wav and plots)')
    args = parser.parse_args()

    # Paths
    CLEAN = args.clean
    WHITE_NOISE = args.noise
    OUT_DIR = args.out_dir
    os.makedirs(OUT_DIR, exist_ok=True)
    NOISY_OUT = os.path.join(OUT_DIR, 'sample_audio_noisy.wav')
    DENOISED_OUT = os.path.join(OUT_DIR, 'sample_audio_denoised.wav')
    PRED_NOISE = os.path.join(OUT_DIR, 'predicted_noise.wav')

    # Read clean
    if not os.path.exists(CLEAN):
        print(f"Missing clean sample: {CLEAN}")
        return

    clean, sr = read_mono(CLEAN)

    # Read or generate noise
    if os.path.exists(WHITE_NOISE):
        noise, sr2 = read_mono(WHITE_NOISE)
        if sr2 != sr:
            print(f"Resampling noise from {sr2} to {sr} is required but not implemented.")
            return
    else:
        # generate small noise on the fly
        print("No white_noise_test.wav found — generating synthetic noise (5s)")
        dur = max(5, len(clean) / sr)
        noise = np.random.normal(0, 1, int(dur * sr)) * 0.05

    # Mix to create noisy
    noisy = mix_noise(clean, noise, noise_level=args.noise_level)
    sf.write(NOISY_OUT, noisy, sr)
    print(f"Wrote noisy file: {NOISY_OUT}")

    # Denoise using AudioDeNoise
    denoiser = AudioDeNoise(NOISY_OUT)
    denoiser.deNoise(DENOISED_OUT)
    print(f"Wrote denoised file: {DENOISED_OUT}")

    # Generate predicted noise file from white noise sample if exists
    if os.path.exists(WHITE_NOISE):
        denoiser.generateNoiseProfileTo(WHITE_NOISE, PRED_NOISE)
        pred_noise, _ = read_mono(PRED_NOISE)
        print(f"Wrote predicted noise: {PRED_NOISE}")
    else:
        pred_noise = noise[: len(clean)]

    # Read outputs to plot
    denoised, _ = read_mono(DENOISED_OUT)

    # Ensure same lengths for plotting
    L = len(clean)
    noisy = noisy[:L]
    denoised = denoised[:L]
    pred_noise = pred_noise[:L]

    signals = {
        'clean': clean,
        'noisy': noisy,
        'denoised': denoised,
        'predicted_noise': pred_noise,
    }

    waveforms_png = os.path.join(OUT_DIR, 'waveforms.png')
    spectrograms_png = os.path.join(OUT_DIR, 'spectrograms.png')
    plot_waveforms(signals, sr, waveforms_png)
    print(f'Saved {waveforms_png}')
    plot_spectrograms(signals, sr, spectrograms_png)
    print(f'Saved {spectrograms_png}')


if __name__ == '__main__':
    main()
