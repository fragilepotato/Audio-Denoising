function deNoiseAudio(inputFile, outputFile)
    % Replicates the Python AudioDeNoise.deNoise method in MATLAB.
    % Reads an audio file in chunks, applies wavelet denoising,
    % and writes the clean signal to an output file.

    % Get audio file info
    info = audioinfo(inputFile);
    rate = info.SampleRate;
    totalSamples = info.TotalSamples;

    % Set chunk size to 10% of total samples, matching Python code
    % int(rate * info.duration * 0.10)
    chunkSize = floor(totalSamples * 0.10);
    if chunkSize == 0
        chunkSize = totalSamples; % Handle very short files
    end

    % Set up audio file reader and writer
    % dsp.AudioFileReader/Writer are ideal for chunk-based processing
    reader = dsp.AudioFileReader(inputFile, 'SamplesPerFrame', chunkSize);
    writer = dsp.AudioFileWriter(outputFile, 'SampleRate', rate, 'FileFormat', 'WAV');

    % --- Set Wavelet Parameters ---
    wname = 'db4'; % Daubechies 4
    level = 2;     % Decomposition level

    % Set wavelet extension mode to 'periodic' to match Python's 'per'
    dwtmode('per', 'nodisplay');
    
    disp('Starting denoising process...');
    
    % Process file chunk by chunk
    while ~isDone(reader)
        % Read a block of audio
        block = reader();
        [numSamples, numChannels] = size(block);
        
        % Pre-allocate output block
        clean_block = zeros(numSamples, numChannels);

        % Process each channel independently
        for ch = 1:numChannels
            channel_data = block(:, ch);

            % 1. Wavelet Decomposition
            [c, l] = wavedec(channel_data, level, wname);

            % 2. Estimate noise standard deviation (sigma)
            % Get finest detail coefficients (D1)
            det1 = detcoef(c, l, 1);
            
            % Calculate Median Absolute Deviation (MAD), matching Python's mad()
            % The '1' signifies median-based MAD (the default)
            sigma = mad(det1, 1); 

            % 3. Calculate VISU Shrink threshold (Universal Threshold)
            % thresh = sigma * sqrt(2 * log(N))
            thresh = sigma * sqrt(2 * log(numSamples));

            % 4. Apply soft thresholding to all detail levels (D1, D2)
            c_thresh = c; % Start with original coefficients
            
            % Get start index of D2 (which is after A2)
            startIndex = l(1) + 1; 
            
            % Loop from finest level (1) to coarsest (level)
            % In the [c,l] structure, details are stored D(level), ..., D(1)
            % But detcoef(c,l,k) gets the k-th level (k=1 is finest)
            % We must loop and place them back correctly.
            
            % We skip the approximation coefficients c(1:l(1))
            % We threshold detail levels D2 (l(2)) and D1 (l(3))
            
            % Threshold D2
            det2 = detcoef(c, l, 2);
            det2_thresh = wthresh(det2, 's', thresh); % 's' for soft
            c_thresh(l(1)+1 : l(1)+l(2)) = det2_thresh;
            
            % Threshold D1
            det1_thresh = wthresh(det1, 's', thresh);
            c_thresh(l(1)+l(2)+1 : l(1)+l(2)+l(3)) = det1_thresh;

            % 5. Reconstruct the clean signal
            clean_channel = waverec(c_thresh, l, wname);
            
            % waverec 'per' mode can sometimes result in a length mismatch by 1 sample
            if length(clean_channel) > numSamples
                clean_channel = clean_channel(1:numSamples);
            elseif length(clean_channel) < numSamples
                clean_channel(end+1:numSamples) = 0; % Pad with zero
            end

            clean_block(:, ch) = clean_channel;
        end
        
        % Write the cleaned block to the output file
        writer(clean_block);
    end
    
    % Clean up resources
    release(reader);
    release(writer);
    
    disp('Denoising complete.');
end