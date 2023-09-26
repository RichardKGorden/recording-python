import pyaudio
import wave

# Initialize PyAudio
audio = pyaudio.PyAudio()

# Define audio recording settings
format = pyaudio.paInt16
channels = 2
sample_rate = 44100
chunk = 1024
audio_duration = 10  # Adjust the duration as needed

# Open an audio stream for recording
audio_stream = audio.open(format=format, channels=channels,
                         rate=sample_rate, input=True,
                         frames_per_buffer=chunk)

# Create a WAV file to save the audio
audio_output_file = "output_audio.wav"
audio_wavefile = wave.open(audio_output_file, 'wb')
audio_wavefile.setnchannels(channels)
audio_wavefile.setsampwidth(audio.get_sample_size(format))
audio_wavefile.setframerate(sample_rate)

# Record audio
print("Recording audio...")
audio_frames = []
for i in range(0, int(sample_rate / chunk * audio_duration)):
    audio_data = audio_stream.read(chunk)
    audio_frames.append(audio_data)
    audio_wavefile.writeframes(audio_data)

# Close audio stream and file
audio_stream.stop_stream()
audio_stream.close()
audio_wavefile.close()
audio.terminate()

print("Audio recording completed.")

# Now you have the audio saved in 'output_audio.wav'
