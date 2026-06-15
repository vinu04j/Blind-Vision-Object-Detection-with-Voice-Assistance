import pyttsx3
from gtts import gTTS
import os
import tempfile
import subprocess
import platform
import threading
import time
import uuid

class VoiceOutput:
    def __init__(self):
        """Initialize voice output engine"""
        self.engine = pyttsx3.init()
        self.engine.setProperty('rate', 150)
        self.engine.setProperty('volume', 0.9)
        
        # Create a dedicated audio folder instead of temp
        self.audio_dir = os.path.join(os.path.expanduser("~"), ".blind_vision_audio")
        if not os.path.exists(self.audio_dir):
            os.makedirs(self.audio_dir)
        
    def speak(self, text, language="en"):
        """Speak the given text"""
        try:
            if language == "ta":
                thread = threading.Thread(target=self._speak_tamil, args=(text,))
                thread.daemon = True
                thread.start()
            else:
                self._speak_english(text)
        except Exception as e:
            print(f"Error in voice output: {e}")
    
    def _speak_english(self, text):
        """Speak in English using pyttsx3"""
        try:
            self.engine.say(text)
            self.engine.runAndWait()
        except Exception as e:
            print(f"Error in English TTS: {e}")
    
    def _speak_tamil(self, text):
        """Speak in Tamil using gTTS with better file handling"""
        try:
            # Generate unique filename to avoid conflicts
            unique_id = str(uuid.uuid4())[:8]
            filename = os.path.join(self.audio_dir, f"tamil_{unique_id}.mp3")
            
            # Generate audio file
            try:
                tts = gTTS(text=text, lang='ta', slow=False)
                tts.save(filename)
            except Exception as e:
                print(f"gTTS save error: {e}")
                return
            
            # Wait a bit for file to be written
            time.sleep(0.1)
            
            # Try to play with different methods
            self._play_audio_safe(filename)
            
            # Clean up file after a delay (generous, since playback is async
            # and longer text takes longer to speak)
            threading.Timer(15.0, lambda: self._cleanup_file(filename)).start()
            
        except Exception as e:
            print(f"Error in Tamil TTS: {e}")
    
    def _play_audio_safe(self, filepath):
        """Play audio file safely without permission issues"""
        try:
            system = platform.system()
            
            if system == 'Windows':
                # Method 1: Use PowerShell with WPF MediaPlayer (supports MP3, unlike
                # winsound / Media.SoundPlayer which only support WAV)
                try:
                    filepath_escaped = filepath.replace("'", "''")
                    ps_command = f'''
                    Add-Type -AssemblyName PresentationCore
                    $player = New-Object System.Windows.Media.MediaPlayer
                    $player.Open([uri]::new('{filepath_escaped}'))
                    Start-Sleep -Milliseconds 300
                    $player.Play()
                    $duration = 5
                    if ($player.NaturalDuration.HasTimeSpan) {{
                        $duration = $player.NaturalDuration.TimeSpan.TotalSeconds + 0.5
                    }}
                    Start-Sleep -Seconds $duration
                    $player.Stop()
                    $player.Close()
                    '''
                    subprocess.Popen(
                        ['powershell', '-NoProfile', '-WindowStyle', 'Hidden', '-Command', ps_command],
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL,
                        creationflags=0x08000000 if system == 'Windows' else 0
                    )
                    return
                except Exception as e1:
                    print(f"PowerShell MediaPlayer failed: {e1}")
                
                # Method 2: Use VLC (if installed)
                try:
                    subprocess.Popen(
                        ['vlc', '--play-and-exit', filepath],
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL
                    )
                    return
                except:
                    pass
            
            elif system == 'Darwin':  # macOS
                subprocess.Popen(
                    ['afplay', filepath],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )
                return
            
            else:  # Linux
                # Try multiple options
                try:
                    subprocess.Popen(
                        ['paplay', filepath],
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL
                    )
                    return
                except:
                    try:
                        subprocess.Popen(
                            ['mpg123', filepath],
                            stdout=subprocess.DEVNULL,
                            stderr=subprocess.DEVNULL
                        )
                        return
                    except:
                        pass
        
        except Exception as e:
            print(f"Error playing audio: {e}")
    
    def _cleanup_file(self, filepath):
        """Clean up audio file after playback"""
        try:
            if os.path.exists(filepath):
                os.remove(filepath)
        except Exception as e:
            print(f"Cleanup error: {e}")
    
    def speak_objects(self, objects, language="en"):
        """Speak detected objects"""
        if not objects:
            self.speak("No objects detected", language)
            return
        
        # Create announcement
        if len(objects) == 1:
            obj = objects[0]
            if language == "ta":
                announcement = f"{obj['name']} உணரப்பட்டுள்ளது"
            else:
                announcement = f"{obj['name']} detected"
        else:
            names = [obj['name'] for obj in objects[:2]]
            if language == "ta":
                announcement = f"{names[0]} மற்றும் {names[1]} உணரப்பட்டுள்ளது"
            else:
                announcement = f"{names[0]} and {names[1]} detected"
        
        self.speak(announcement, language)
    
    def alert_obstacle(self, language="en"):
        """Alert about close obstacle"""
        if language == "ta":
            self.speak("எச்சரிக்கை! பொருள் மிக நெருக்கமாக உள்ளது", language)
        else:
            self.speak("Warning! Object very close", language)