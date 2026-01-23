# Source - https://stackoverflow.com/a
# Posted by siddhantsomani, modified by community. See post 'Timeline' for change history
# Retrieved 2026-01-23, License - CC BY-SA 4.0

from pydub import AudioSegment
 #Exports to a wav file in the current path.

def generate_single_audio(audio_path: str, single_audio_path : str, start_time : float, end_time : float):
    t1 = start_time * 1000 #Works in milliseconds
    t2 = end_time * 1000
    newAudio = AudioSegment.from_wav(audio_path)
    newAudio = newAudio[t1:t2]
    newAudio.export(single_audio_path, format="wav") #Exports to a wav file in the current path.



