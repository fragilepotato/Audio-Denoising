function extractNoise(noiseSampleFile, outputNoiseFile)
    % This function is an *alternative* to 'generateNoiseProfileTo'.
    % It estimates the noise from 'noiseSampleFile' using the same
    % wavelet thresholding as 'deNoiseAudio' and saves the
    % *removed noise* to 'outputNoiseFile'.

    % Read the entire noise sample (assumed to be small per Python docs)
    [data, rate] = audioread(noiseSampleFile);
    
    [numSamples, numChannels] = size(data);
    extracted_noise = zeros(numSamples, numChannels); % Pre-allocate

    % --- Set Wavelet Parameters ---
    wname = 'db4';
    level = 2;
    dwtmode('per', 'nodisplay');
    
    disp('Starting noise extraction...');

    for ch = 1:numChannels
        channel_data = data(:, ch);

        % 1. Decompose
        [c, l] = wavedec(channel_data, level, wname);

        % 2. Estimate noise
        det1 = detcoef(c, l, 1);
        sigma = mad(det1, 1);

        % 3. Calculate threshold
        thresh = sigma * sqrt(2 * log(numSamples));

        % 4. Create a coefficient vector for the *noise*
        % The noise is the part of the signal we *remove*
        c_noise = zeros(size(c)); % Start with all zeros
        
        % We only care about detail coefficients
        
        % Process D2
        det2 = detcoef(c, l, 2);
        det2_thresh = wthresh(det2, 's', thresh);
        noise_comp_2 = det2 - det2_thresh; % Noise = Original - Cleaned
        c_noise(l(1)+1 : l(1)+l(2)) = noise_comp_2;
        
        % Process D1
        det1_thresh = wthresh(det1, 's', thresh);
        noise_comp_1 = det1 - det1_thresh; % Noise = Original - Cleaned
        c_noise(l(1)+l(2)+1 : l(1)+l(2)+l(3)) = noise_comp_1;
        
        % 5. Reconstruct the noise signal from the noise-only coefficients
        noise_channel = waverec(c_noise, l, wname);
        
        % Fix length mismatch
        if length(noise_channel) > numSamples
            noise_channel = noise_channel(1:numSamples);
        elseif length(noise_channel) < numSamples
            noise_channel(end+1:numSamples) = 0;
        end
        
        extracted_noise(:, ch) = noise_channel;
    end

    % Write the extracted noise to the output file
    audiowrite(outputNoiseFile, extracted_noise, rate);
    disp('Noise extraction complete.');
end