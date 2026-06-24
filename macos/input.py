"""
Input simulation wrapper using pyobjc.
Provides safe mouse click and keyboard input simulation.
"""

import time
from typing import Dict, Optional

from Quartz import (
    CGEventCreateMouseEvent,
    CGEventCreateKeyboardEvent,
    CGEventSetFlags,
    CGEventPost,
    kCGEventLeftMouseDown,
    kCGEventLeftMouseUp,
    kCGEventRightMouseDown,
    kCGEventRightMouseUp,
    kCGEventMouseMoved,
    kCGMouseButtonLeft,
    kCGMouseButtonRight,
    kCGHIDEventTap,
    kCGEventFlagMaskCommand,
    kCGEventFlagMaskAlternate,
    kCGEventFlagMaskControl,
    kCGEventFlagMaskShift,
)

import ApplicationServices as AppServices


# Key code mapping for common keys
KEY_CODES = {
    "return": 36,
    "tab": 48,
    "space": 49,
    "delete": 51,
    "escape": 53,
    "left": 123,
    "right": 124,
    "down": 125,
    "up": 126,
    "f1": 122,
    "f2": 120,
    "f3": 99,
    "f4": 118,
    "f5": 96,
    "f6": 97,
    "f7": 98,
    "f8": 100,
    "f9": 101,
    "f10": 109,
    "f11": 103,
    "f12": 111,
    # Letters (lowercase)
    "a": 0, "s": 1, "d": 2, "f": 3, "h": 4, "g": 5, "z": 6, "x": 7,
    "c": 8, "v": 9, "b": 11, "q": 12, "w": 13, "e": 14, "r": 15,
    "y": 16, "t": 17, "o": 31, "u": 32, "i": 34, "p": 35, "l": 37,
    "j": 38, "k": 40, "n": 45, "m": 46,
    # Numbers
    "0": 29, "1": 18, "2": 19, "3": 20, "4": 21, "5": 23,
    "6": 22, "7": 26, "8": 28, "9": 25,
    # Symbols
    "-": 27, "=": 24, "[": 33, "]": 30, "\\": 42,
    ";": 41, "'": 39, ",": 43, ".": 47, "/": 44, "`": 50,
}

MODIFIER_FLAGS = {
    "cmd": kCGEventFlagMaskCommand,
    "command": kCGEventFlagMaskCommand,
    "alt": kCGEventFlagMaskAlternate,
    "option": kCGEventFlagMaskAlternate,
    "opt": kCGEventFlagMaskAlternate,
    "ctrl": kCGEventFlagMaskControl,
    "control": kCGEventFlagMaskControl,
    "shift": kCGEventFlagMaskShift,
}


class InputSimulator:
    """
    Simulates user input (mouse clicks, keyboard events) using Quartz.
    All events are posted at the HID event tap level for system-wide effect.
    """

    def __init__(self):
        pass

    def click_at(self, x: int, y: int, button: str = "left") -> Dict[str, str]:
        """
        Simulate a mouse click at the specified screen coordinates.
        
        Args:
            x: Screen X coordinate.
            y: Screen Y coordinate.
            button: "left" or "right".
        
        Returns: {"status": "success"} or {"error": "..."}
        """
        try:
            point = (x, y)
            
            if button == "right":
                event_type_down = kCGEventRightMouseDown
                event_type_up = kCGEventRightMouseUp
                mouse_button = kCGMouseButtonRight
            else:
                event_type_down = kCGEventLeftMouseDown
                event_type_up = kCGEventLeftMouseUp
                mouse_button = kCGMouseButtonLeft
            
            # Create mouse down event
            event_down = CGEventCreateMouseEvent(
                None,
                event_type_down,
                point,
                mouse_button
            )
            
            # Create mouse up event
            event_up = CGEventCreateMouseEvent(
                None,
                event_type_up,
                point,
                mouse_button
            )
            
            # Post events to the system
            CGEventPost(kCGHIDEventTap, event_down)
            time.sleep(0.05)  # Small delay between down and up
            CGEventPost(kCGHIDEventTap, event_up)
            
            return {"status": "success", "x": x, "y": y, "button": button}
        
        except Exception as e:
            return {"error": str(e)}

    def double_click_at(self, x: int, y: int) -> Dict[str, str]:
        """
        Simulate a double-click at the specified screen coordinates.
        
        Args:
            x: Screen X coordinate.
            y: Screen Y coordinate.
        
        Returns: {"status": "success"} or {"error": "..."}
        """
        try:
            point = (x, y)
            
            # Create first click
            event1_down = CGEventCreateMouseEvent(
                None, kCGEventLeftMouseDown, point, kCGMouseButtonLeft
            )
            event1_up = CGEventCreateMouseEvent(
                None, kCGEventLeftMouseUp, point, kCGMouseButtonLeft
            )
            
            # Create second click
            event2_down = CGEventCreateMouseEvent(
                None, kCGEventLeftMouseDown, point, kCGMouseButtonLeft
            )
            event2_up = CGEventCreateMouseEvent(
                None, kCGEventLeftMouseUp, point, kCGMouseButtonLeft
            )
            
            # Post all events with small delays
            CGEventPost(kCGHIDEventTap, event1_down)
            time.sleep(0.02)
            CGEventPost(kCGHIDEventTap, event1_up)
            time.sleep(0.02)
            CGEventPost(kCGHIDEventTap, event2_down)
            time.sleep(0.02)
            CGEventPost(kCGHIDEventTap, event2_up)
            
            return {"status": "success", "x": x, "y": y, "clicks": 2}
        
        except Exception as e:
            return {"error": str(e)}

    def type_string(self, text: str, delay: float = 0.02) -> Dict[str, str]:
        """
        Type a string character by character using keyboard events.
        
        Args:
            text: The string to type.
            delay: Delay between keystrokes (seconds).
        
        Returns: {"status": "success", "length": int} or {"error": "..."}
        """
        try:
            for char in text:
                # Get the key code for this character
                key_code = KEY_CODES.get(char.lower())
                
                if key_code is None:
                    # For characters not in our map, skip (safety fallback)
                    continue
                
                # Determine if shift is needed (uppercase or symbols)
                needs_shift = char.isupper() or char in '~!@#$%^&*()_+{}|:"<>?'
                
                # Create key down event
                event_down = CGEventCreateKeyboardEvent(None, key_code, True)
                
                # Create key up event
                event_up = CGEventCreateKeyboardEvent(None, key_code, False)
                
                # Set shift flag if needed
                if needs_shift:
                    CGEventSetFlags(event_down, kCGEventFlagMaskShift)
                    CGEventSetFlags(event_up, kCGEventFlagMaskShift)
                
                # Post events
                CGEventPost(kCGHIDEventTap, event_down)
                time.sleep(delay)
                CGEventPost(kCGHIDEventTap, event_up)
                time.sleep(delay)
            
            return {"status": "success", "length": len(text)}
        
        except Exception as e:
            return {"error": str(e)}

    def press_key(self, key_combination: str) -> Dict[str, str]:
        """
        Press a key or key combination.
        
        Args:
            key_combination: Key combo string, e.g., "cmd+tab", "ctrl+c", "enter".
                             Modifiers: cmd, alt/option, ctrl, shift.
                             Keys: letters, numbers, return, tab, space, delete, escape,
                                   arrows (left, right, up, down), f1-f12.
        
        Returns: {"status": "success"} or {"error": "..."}
        """
        try:
            parts = key_combination.lower().split("+")
            
            # Separate modifiers from the main key
            modifiers = []
            main_key = None
            
            for part in parts:
                if part in MODIFIER_FLAGS:
                    modifiers.append(MODIFIER_FLAGS[part])
                elif part in KEY_CODES:
                    main_key = part
                else:
                    return {"error": f"Unknown key: {part}"}
            
            if main_key is None:
                return {"error": "No main key specified in combination"}
            
            key_code = KEY_CODES[main_key]
            
            # Calculate combined modifier flags
            flags = 0
            for flag in modifiers:
                flags |= flag
            
            # Create key down event
            event_down = CGEventCreateKeyboardEvent(None, key_code, True)
            CGEventSetFlags(event_down, flags)
            
            # Create key up event
            event_up = CGEventCreateKeyboardEvent(None, key_code, False)
            CGEventSetFlags(event_up, flags)
            
            # Post events
            CGEventPost(kCGHIDEventTap, event_down)
            time.sleep(0.02)
            CGEventPost(kCGHIDEventTap, event_up)
            
            return {"status": "success", "combination": key_combination}
        
        except Exception as e:
            return {"error": str(e)}
