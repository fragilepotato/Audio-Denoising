from denoise import AudioDeNoise
import os

# Sample file names
INPUT_AUDIO = "sample_audio.wav"
REQUESTED_NOISE_SAMPLE = "input_noise_profile.wav"
FALLBACK_NOISE_SAMPLE = "white_noise_test.wav"

OUT_DIR = "outputs"
os.makedirs(OUT_DIR, exist_ok=True)
OUTPUT_DENOISED = os.path.join(OUT_DIR, "input_denoised.wav")
OUTPUT_NOISE = os.path.join(OUT_DIR, "input_noise_output.wav")

audioDenoiser = AudioDeNoise(inputFile=INPUT_AUDIO)
audioDenoiser.deNoise(outputFile=OUTPUT_DENOISED)

# Use the requested noise sample if it exists, otherwise fall back to a repo test file
noise_sample = REQUESTED_NOISE_SAMPLE if os.path.exists(REQUESTED_NOISE_SAMPLE) else FALLBACK_NOISE_SAMPLE
print(f"Using noise sample: {noise_sample}")
audioDenoiser.generateNoiseProfileTo(noiseFile=noise_sample, outputFile=OUTPUT_NOISE)