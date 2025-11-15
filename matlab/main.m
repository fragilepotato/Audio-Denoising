%% Wavelet Audio Denoising Demo (MATLAB)
% This script shows two ways to denoise audio using wavelets:
%  1) Direct denoising with wdenoise (single-shot)
%  2) Chunked denoising using deNoiseAudio (replicates the Python approach)
% It also plots time-domain and spectrogram views of original/noisy/denoised.

clc; close all;

%% Resolve project paths
thisFile = mfilename('fullpath');
matlabDir = fileparts(thisFile);
projectRoot = fileparts(matlabDir);

inputClean = fullfile(projectRoot, 'sample_audio.wav');           % required
inputNoiseSample = fullfile(projectRoot, 'white_noise_test.wav'); % optional

% Ensure outputs folder exists
outputDir = fullfile(projectRoot, 'outputs');
if ~exist(outputDir, 'dir'), mkdir(outputDir); end

outNoisy = fullfile(outputDir, 'sample_audio_noisy_matlab.wav');
outDenoised_wdenoise = fullfile(outputDir, 'sample_audio_denoised_wdenoise.wav');
outDenoised_chunked = fullfile(outputDir, 'sample_audio_denoised_matlab.wav');
outPredictedNoise = fullfile(outputDir, 'predicted_noise_matlab.wav');

%% Configuration
WAVELET_NAME = 'db4';
LEVEL = 2;                 % Decomposition level (matches project defaults)
ADD_SYNTH_NOISE = true;    % Set true to mix in noise to clearly hear denoising
NOISE_LEVEL = 0.15;        % Noise scale (0.05 subtle, 0.15 clear, 0.3 strong)

%% Load input
assert(isfile(inputClean), sprintf('Input audio not found: %s', inputClean));
[x, fs] = audioread(inputClean);

% If stereo, use first channel for visualization and wdenoise; deNoiseAudio handles multi-channel
if size(x,2) > 1
	x_mono = x(:,1);
else
	x_mono = x;
end

% Treat input as already noisy by default. If you want to synthesize noise,
% you can mix externally (see white_noise.py) or modify this script.
% Default: treat input as already noisy; optionally override below
noisy = x_mono;
if ADD_SYNTH_NOISE
	% Try to use a provided noise sample; otherwise generate white noise
	if isfile(inputNoiseSample)
		[n, fsN] = audioread(inputNoiseSample);
		if size(n,2) > 1, n = n(:,1); end
		if fsN ~= fs
			warning('Noise sample rate differs (fsN=%d vs fs=%d). Using white noise instead.', fsN, fs);
			n = randn(size(x_mono));
		else
			% match length by tiling or truncating
			if length(n) < length(x_mono)
				reps = ceil(length(x_mono)/length(n));
				n = repmat(n, reps, 1);
			end
			n = n(1:length(x_mono));
		end
	else
		n = randn(size(x_mono));
	end
	% normalize noise and mix
	n = n ./ max(abs(n)+eps);
	noisy = x_mono + NOISE_LEVEL * n;
	% prevent clipping
	m = max(abs(noisy)); if m > 1, noisy = noisy ./ m; end
	audiowrite(outNoisy, noisy, fs);
	fprintf('Wrote synthetic noisy file: %s\n', outNoisy);
end

%% 1) Denoise with wdenoise (single-shot)
% Matches the documentation example style using the decimated DWT.
xd = wdenoise(noisy, LEVEL, 'Wavelet', WAVELET_NAME);
audiowrite(outDenoised_wdenoise, xd, fs);
fprintf('Wrote: %s\n', outDenoised_wdenoise);

%% 2) Denoise with chunked processing (replicates Python)
% Uses deNoiseAudio.m which processes in 10%% chunks and does VISU shrink per chunk.
try
	denoiseInputPath = inputClean;
	if ADD_SYNTH_NOISE && exist(outNoisy,'file')
		denoiseInputPath = outNoisy;
	end
	deNoiseAudio(denoiseInputPath, outDenoised_chunked);
	fprintf('Wrote: %s\n', outDenoised_chunked);
catch ME
	warning(ME.identifier, '%s\nFalling back to wdenoise result only.', ME.message);
end

%% Optional: create predicted noise from a noise-only sample
if isfile(inputNoiseSample)
	try
		extractNoise(inputNoiseSample, outPredictedNoise);
		fprintf('Wrote: %s\n', outPredictedNoise);
	catch ME
		warning(ME.identifier, '%s', ME.message);
	end
else
	fprintf('No noise sample found at %s (skipping noise extraction).\n', inputNoiseSample);
end


%% Visualization (time domain)
t = (0:length(x_mono)-1)/fs;
figure('Name','Wavelet Denoising - Time Domain','Position',[100 100 1200 700]);
subplot(3,1,1); plot(t, x_mono); title('Original (mono)'); xlabel('Time (s)'); ylabel('Amp'); xlim([0 t(end)]);
subplot(3,1,2); plot(t, noisy(1:length(t))); title('Noisy (or input-as-is)'); xlabel('Time (s)'); ylabel('Amp'); xlim([0 t(end)]);
subplot(3,1,3); plot(t, xd(1:length(t))); title(sprintf('Denoised (wdenoise, %s, L=%d)', WAVELET_NAME, LEVEL)); xlabel('Time (s)'); ylabel('Amp'); xlim([0 t(end)]);

%% Visualization (spectrograms)
figure('Name','Wavelet Denoising - Spectrograms','Position',[150 150 1200 900]);
subplot(3,1,1); spectrogram(x_mono, 1024, 512, 1024, fs, 'yaxis'); title('Original (mono)');
subplot(3,1,2); spectrogram(noisy(1:length(t)), 1024, 512, 1024, fs, 'yaxis'); title('Noisy (or input-as-is)');
subplot(3,1,3); spectrogram(xd(1:length(t)), 1024, 512, 1024, fs, 'yaxis'); title('Denoised (wdenoise)');

disp('Done. See written WAV files and figures.');

%% Playback (hear before/after)
% Play short excerpts so you can hear the difference quickly.
try
	PLAY_SECONDS = 8; % change if you want longer/shorter previews
	segN = min(round(PLAY_SECONDS * fs), length(x_mono));
	idx = 1:segN;

	fprintf('\nPlayback preview (~%d s each)\n', round(segN/fs));
	fprintf('Press Enter to play: Original (noisy)\n');
	input('', 's');
	soundsc(noisy(idx), fs);
	pause(segN/fs + 0.5);

	fprintf('Press Enter to play: Denoised (wdenoise)\n');
	input('', 's');
	soundsc(xd(idx), fs);
	pause(segN/fs + 0.5);

	% If chunked output file exists, play that too
	if exist(outDenoised_chunked, 'file')
		[xd_chunk, fs2] = audioread(outDenoised_chunked);
		if size(xd_chunk,2) > 1, xd_chunk = xd_chunk(:,1); end
		if fs2 == fs
			segN2 = min(segN, length(xd_chunk));
			fprintf('Press Enter to play: Denoised (chunked)\n');
			input('', 's');
			soundsc(xd_chunk(1:segN2), fs);
			pause(segN2/fs + 0.5);
		else
			warning('Chunked output samplerate differs (fs=%d vs %d). Skipping chunked playback.', fs2, fs);
		end
	end
catch ME
	warning(ME.identifier, 'Playback skipped: %s', ME.message);
end