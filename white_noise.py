import numpy as np
import soundfile as sf

def generate_white_noise_wav(filename: str, duration_seconds: float, samplerate: int, channels: int = 1, amplitude: float = 0.5):
    """
    Generates Additive White Gaussian Noise (AWGN) and saves it as a WAV file.

    Parameters
    ----------
    filename : str
        The name of the output WAV file.
    duration_seconds : float
        The duration of the noise in seconds.
    samplerate : int
        The sampling rate (e.g., 44100 Hz).
    channels : int, optional
        The number of audio channels (1 for mono, 2 for stereo). Defaults to 1.
    amplitude : float, optional
        The peak amplitude of the noise (0.0 to 1.0). Defaults to 0.5.
    """
    # Calculate the total number of samples
    num_samples = int(samplerate * duration_seconds)

    # Generate white noise (samples from a standard normal distribution)
    # The 'normal' function creates Additive White Gaussian Noise (AWGN).
    noise_signal = np.random.normal(0, 1, (num_samples, channels))

    # Scale the signal to the desired amplitude range.
    # The scaling uses the maximum absolute value of the signal to ensure the
    # peak amplitude doesn't exceed 1.0, preventing clipping.
    noise_signal = (noise_signal / np.max(np.abs(noise_signal))) * amplitude
    
    # Write the numpy array to a WAV file
    sf.write(filename, noise_signal, samplerate)
    print(f"✅ Generated white noise file: {filename}")


if __name__ == '__main__':
    # --- Parameters for the Noise File ---
    OUTPUT_FILE = "white_noise_test.wav"
    SAMPLE_RATE = 44100  # Standard audio sample rate
    DURATION = 5.0       # 5 seconds of noise
    CHANNELS = 1         # Mono audio
    AMPLITUDE = 0.06      # Peak amplitude (max is 1.0)
    # -------------------------------------

    generate_white_noise_wav(OUTPUT_FILE, DURATION, SAMPLE_RATE, CHANNELS, AMPLITUDE)

    # You can now use this file with your AudioDeNoise class:
    # from your_module import AudioDeNoise
    # audioDenoiser = AudioDeNoise(OUTPUT_FILE)
    # audioDenoiser.deNoise("denoised_output.wav")