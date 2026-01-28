import logging
from typing import Optional, Callable, List
from constants import VOICE_ENABLED, VOICE_TIMEOUT, VOICE_RATE, VOICE_VOLUME
from exceptions import VoiceError

logger = logging.getLogger(__name__)

class VoiceInterface:
    """Voice interaction interface."""
    
    def __init__(self):
        self.is_available = self._check_availability()
        self.callbacks: List[Callable] = []
        self.enabled = VOICE_ENABLED and self.is_available
        
    def _check_availability(self) -> bool:
        """Check if voice is available."""
        try:
            import speech_recognition
            import pyttsx3
            logger.info("Voice libraries available")
            return True
        except ImportError:
            logger.warning("Voice libraries not available (speech-recognition, pyttsx3)")
            return False
    
    def listen(self) -> Optional[str]:
        """Listen for voice input."""
        if not self.enabled:
            logger.info("Voice input not available or disabled")
            return None
        
        try:
            import speech_recognition as sr
            recognizer = sr.Recognizer()
            with sr.Microphone() as source:
                logger.info("Listening for audio...")
                audio = recognizer.listen(source, timeout=VOICE_TIMEOUT)
                text = recognizer.recognize_google(audio)
                logger.info(f"Heard: {text}")
                return text
        except Exception as e:
            logger.error(f"Voice listen failed: {e}")
            raise VoiceError(f"Voice listen failed: {e}")
    
    def speak(self, text: str):
        """Speak text."""
        if not self.enabled:
            logger.info(f"Would speak: {text[:50]}...")
            return
        
        try:
            import pyttsx3
            engine = pyttsx3.init()
            engine.setProperty('rate', VOICE_RATE)
            engine.setProperty('volume', VOICE_VOLUME)
            engine.say(text)
            engine.runAndWait()
            logger.info(f"Spoke: {text[:50]}...")
        except Exception as e:
            logger.error(f"Voice speak failed: {e}")
            raise VoiceError(f"Voice speak failed: {e}")
    
    def register_callback(self, callback: Callable):
        """Register callback for voice commands."""
        self.callbacks.append(callback)
        logger.info("Voice callback registered")
    
    def get_stats(self) -> dict:
        """Get voice statistics."""
        return {
            "available": self.is_available,
            "enabled": self.enabled,
            "callbacks": len(self.callbacks)
        }
