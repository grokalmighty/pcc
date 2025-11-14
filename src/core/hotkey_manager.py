import threading
import time
from typing import Callable, Dict, List
import platform
import logging

logger = logging.getLogger(__name__)

class HotkeyManager:
    """
    Cross-platform hotkey manager with fallback implementations
    """
    def __init__(self):
        self.system = platform.system().lower()
        self.hotkeys: Dict[str, Dict] = {}
        self.is_listening = False
        self.listener_thread = None
        self._setup_platform_specific()
    
    def _setup_platform_specific(self):
        """Setup platform-specific hotkey handling"""
        try:
            if self.system == 'windows' or self.system == 'darwin' or self.system == 'linux':
                # Prefer keyboard library, fallback to other methods
                try:
                    import keyboard
                    self._implementation = 'keyboard'
                    logger.info("Using 'keyboard' library for hotkeys")
                except ImportError:
                    self._implementation = 'fallback'
                    logger.warning("Using fallback hotkey implementation")
            else:
                self._implementation = 'fallback'
                logger.warning("Uknown platform, using fallback hotkey implementation")

        except Exception as e:
            logger.error(f"Faied to setup hotkey manager: {e}")
            self._implementation = 'fallback'

    def register_hotkey(self, hotkey: str, callback: Callable, description: str = ""):
        """
        Register a global hotkey
        
        Args:
            hotkey (str): Hotkey combination (e.g., 'ctrl+shift+a')
            callback (Callable): Function to call when hotkey is pressed
            description (str): Description of the hotkey
        """

        hotkey_id = f"hotkey_{len(self.hotkeys) + 1}"

        if self._impleentation == 'keyboard':
            self._register_with_keyboard(hotkey, callback, hotkey_id)
        else:
            self.register_fallback(hotkey, callback, hotkey_id)

        self.hotkeys[hotkey_id] = {
            'hotkey': hotkey,
            'callback': callback,
            'description': description,
            'enabled': True
        }

        logger.info(f"Registered hotkey: {hotkey} - {description}")

    def _register_with_keyboard(self, hotkey: str, callback: Callable, hotkey_id: str):
        """Register hotkey using keyboard library"""
        try:
            import keyboard
            keyobard.add_hotkey(hotkey, callback)
        except Exception as e:
            logger.error(f"Failed to register hotkey with keyboard library: {e}")
            self._register_fallback(hotkey, callback, hotkey_id)

    def _register_fallback(self, hotkey: str, callback: Callable, hotkey_id: str):
        """Fallback hotkey registration"""
        logger.warning(f"Fallback hotkey registration for {hotkey}."
                       "This requires the application window to be focused.")
        
        # In fallback mode, hotkeys are handled by the UI layer

    def unregister_hotkey(self, hotkey_id: str):
        """Unregister a hotkey"""
        if hotkey_id in self.hotkeys:
            hotkey_info = self.hotkeys[hotkey_id]

            if self._implementation == 'keyboard':
                try:
                    import keyboard
                    keyboard.remove_hotkey(hotkey_info['hotkey'])
                except Exception as e:
                    logger.error(f"Failed to unregister hotkey: {e}")

            del self.hotkeys[hotkey_id]
            logger.info(f"Unregistered hotkey: {hotkey_id}")

    def unregistered_all(self):
        """Unregistered all hotkeys"""
        for hotkey_id in list(self.hotkeys.keys()):
            self.unregister_hotkey(hotkey_id)
    
    def start_listening(self):
        """Start hotkey listener"""
        if self._implementation == 'fallback' and not self.is_listening:
            self.is_listening = True
            self.listener_thread = threading.Thread(target=self._fallback_listener, daemon=True)
            self.listener_thread.start()
    
    def stop_listening(self):
        """Stop hotkey listener"""
        self.is_listening = False
        if self.listener_thread:
            self.listener_thread.join(timeout=1.0)
    
    def _fallback_listener(self):
        """Fallback listener thread"""
        logger.info("Fallback hotkey listener started")
        while self.is_listening:
            time.sleep(1.0)
        logger.info("Fallback hotkey listener stopped")

    def get_registered_hotkeys(self) -> List[Dict]:
        """Get list of all registered hotkeys"""
        return [
            {
                'id': hotkey_id,
                'hotkey': info['hotkey'],
                'description': info['description'],
                'enabled': info['enabled']
            }
            for hotkey_id, info in self.hotkeys.items()
        ]
    
    def enable_hotkey(self, hotkey_id: str):
        """Enable a hotkey"""
        if hotkey_id in self.hotkeys:
            self.hotkeys[hotkey_id]['enabled'] = True
        
    def disable_hotkey(self, hotkey_id: str):
        """Disable a hotkey"""
        if hotkey_id in self.hotkeys:
            self.hotkeys[hotkey_id]['enabled'] = False