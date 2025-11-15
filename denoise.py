"""
This class has two main functions

    - De-noising the file (pywt does it)
    - Creating a Noise Profile (parses the signal and creates a profile very memory heavy)
"""

import numpy as np
import pywt
import soundfile
from tqdm import tqdm
import os
import traceback

from lib.noiseProfiler import NoiseProfiler


def mad(arr):
    """ Median Absolute Deviation: a "Robust" version of standard deviation.
        Indices variability of the sample.
        https://en.wikipedia.org/wiki/Median_absolute_deviation 
    """
    arr = np.ma.array(arr).compressed()
    med = np.median(arr)
    return np.median(np.abs(arr - med))


class AudioDeNoise:
    """
    Class to de-noise the audio signal. The audio file is read in chunks and processed,
    cleaned and appended to the output file..

    It can de-noise multiple channels, any sized file, formats supported by soundfile

    Wavelets used ::
        Daubechies 4 : db4
        Level : decided by pyWavelets

    Attributes
    ----------
    __inputFile : str
        name of the input audio file

    Examples
    --------
    To de noise an audio file

    >>> audioDenoiser = AudioDeNoise("input.wav")
    >>> audioDenoiser.deNoise("input_denoised.wav")

    To generate the noise profile

    >>> audioDenoiser = AudioDeNoise("input.wav")
    >>> audioDenoiser.generateNoiseProfile("input_noise_profile.wav")
    """

    def __init__(self, inputFile):
        self.__inputFile = inputFile
        self.__noiseProfile = None

    def deNoise(self, outputFile):
        """
        De-noising function that reads the audio signal in chunks and processes
        and writes to the output file efficiently.

        VISU Shrink is used to generate the noise threshold

        Parameters
        ----------
        outputFile : str
            de-noised file name

        """
        info = soundfile.info(self.__inputFile)  # getting info of the audio
        rate = info.samplerate

        with soundfile.SoundFile(outputFile, "w", samplerate=rate, channels=info.channels) as of:
            for block in tqdm(soundfile.blocks(self.__inputFile, int(rate * info.duration * 0.10))):
                coefficients = pywt.wavedec(block, 'db4', mode='per', level=2)

                #  getting variance of the input signal
                sigma = mad(coefficients[- 1])

                # VISU Shrink thresholding by applying the universal threshold proposed by Donoho and Johnstone
                thresh = sigma * np.sqrt(2 * np.log(len(block)))

                # thresholding using the noise threshold generated
                coefficients[1:] = (pywt.threshold(i, value=thresh, mode='soft') for i in coefficients[1:])

                # getting the clean signal as in original form and writing to the file
                clean = pywt.waverec(coefficients, 'db4', mode='per')
                of.write(clean)

    def generateNoiseProfile(self, noiseFile):
        """
        Parses the input signal and generate the noise profile using wavelet helper
        Look into lib modules to see how the parsing is done

        NOTE: Heavy on the memory, suitable for small files.

        Parameters
        ----------
        noiseFile : str
            name for the noise signal extracted
        """
        # keep legacy behavior but validate file first
        if not os.path.exists(noiseFile):
            raise FileNotFoundError(f"Noise sample not found: {noiseFile}")

        try:
            data, rate = soundfile.read(noiseFile)
        except Exception as exc:
            # surface a clearer error message for libsndfile failures
            raise RuntimeError(f"Could not read noise sample '{noiseFile}': {exc}") from exc

        self.__noiseProfile = NoiseProfiler(data)
        noiseSignal = self.__noiseProfile.getNoiseDataPredicted()

        # overwrite the source (legacy behavior)
        soundfile.write(noiseFile, noiseSignal, rate)

    def generateNoiseProfileTo(self, noiseFile, outputFile):
        """
        Generate a predicted noise signal from `noiseFile` and write it to
        `outputFile`. This is a safer alternative to `generateNoiseProfile` which
        overwrites the source file.

        Parameters
        ----------
        noiseFile : str
            Path to a noise-only audio sample to analyze.
        outputFile : str
            Path where the predicted noise signal will be written.
        """
        if not os.path.exists(noiseFile):
            raise FileNotFoundError(f"Noise sample not found: {noiseFile}")

        try:
            data, rate = soundfile.read(noiseFile)
        except Exception as exc:
            raise RuntimeError(f"Could not read noise sample '{noiseFile}': {exc}") from exc

        self.__noiseProfile = NoiseProfiler(data)
        noiseSignal = self.__noiseProfile.getNoiseDataPredicted()

        # write predicted noise to the requested output file
        try:
            soundfile.write(outputFile, noiseSignal, rate)
        except Exception as exc:
            raise RuntimeError(f"Could not write predicted noise to '{outputFile}': {exc}") from exc

    def __del__(self):
        """
        clean up
        """
        del self.__noiseProfile


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Audio denoising helpers')
    sub = parser.add_subparsers(dest='cmd')

    p_dn = sub.add_parser('denoise', help='Denoise an input file')
    p_dn.add_argument('input', help='Input audio file')
    p_dn.add_argument('output', help='Output denoised audio file')

    p_np = sub.add_parser('noise-profile', help='Generate predicted noise from a noise sample')
    p_np.add_argument('noise_sample', help='Input noise-only sample file')
    p_np.add_argument('output', help='Output file to write predicted noise to')

    args = parser.parse_args()
    if args.cmd == 'denoise':
        d = AudioDeNoise(args.input)
        d.deNoise(args.output)
    elif args.cmd == 'noise-profile':
        d = AudioDeNoise(args.noise_sample)
        d.generateNoiseProfileTo(args.noise_sample, args.output)
