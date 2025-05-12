import time
import logging
import os
from datetime import datetime

class Logger:
    # Class-level variable to track if logger is already initialized
    _is_initialized = False
    
    # Messages that should be filtered out (partial matches)
    FILTERED_MESSAGES = [
        "Using Firefox profile at:",
        "=== Starting Firefox with Persistent Profile ===",
        "Initializing Firefox WebDriver"
    ]
    
    def __init__(self, log_file="mca_automation.log", debug=False, console_output=True, log_to_file=True):
        """
        Initialize logger with file and console handlers
        
        Args:
            log_file: Path to the log file
            debug: Whether to enable debug logging
            console_output: Whether to output logs to console
            log_to_file: Whether to write logs to file
        """
        self.logger = logging.getLogger("MCA_Automation")
        self.debug_mode = debug
        
        # Only set up handlers if this is the first instance
        if not Logger._is_initialized:
            # Clear any existing handlers to avoid duplication
            if self.logger.hasHandlers():
                self.logger.handlers.clear()
            
            # Set log level based on debug mode
            log_level = logging.DEBUG if debug else logging.INFO
            self.logger.setLevel(log_level)
            
            # Prevent propagation to ancestor loggers
            self.logger.propagate = False
            
            # Create formatter
            formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s')
            
            # Add file handler if log_to_file is True
            if log_to_file:
                # Create log directory if it doesn't exist
                log_dir = os.path.dirname(os.path.abspath(log_file))
                if log_dir and not os.path.exists(log_dir):
                    os.makedirs(log_dir, exist_ok=True)
                
                # Create file handler
                file_handler = logging.FileHandler(log_file, encoding='utf-8')
                file_handler.setLevel(log_level)
                file_handler.setFormatter(formatter)
                file_handler.addFilter(self.filter_unwanted_messages)
                self.logger.addHandler(file_handler)
            
            # Add console handler if console_output is True
            if console_output:
                # Create console handler
                console_handler = logging.StreamHandler()
                console_handler.setLevel(log_level)
                console_handler.setFormatter(formatter)
                console_handler.addFilter(self.filter_unwanted_messages)
                self.logger.addHandler(console_handler)
            
            # Mark as initialized
            Logger._is_initialized = True
    
    def filter_unwanted_messages(self, record):
        """Filter out unwanted messages"""
        if record.levelno >= logging.WARNING:
            # Always show warnings and errors
            return True
        
        # Check if message contains any filtered phrases
        for filtered_msg in self.FILTERED_MESSAGES:
            if filtered_msg in record.getMessage():
                return False
        
        return True
    
    def set_debug(self, debug_mode):
        """Set debug mode on or off"""
        self.debug_mode = debug_mode
        new_level = logging.DEBUG if debug_mode else logging.INFO
        
        # Update logger level
        self.logger.setLevel(new_level)
        
        # Update handler levels
        for handler in self.logger.handlers:
            handler.setLevel(new_level)
    
    def log(self, message, level="info"):
        """Log message with timestamp and level"""
        level = level.upper()
        if level == "INFO":
            self.logger.info(message)
        elif level == "ERROR":
            self.logger.error(message)
        elif level == "WARNING":
            self.logger.warning(message)
        elif level == "DEBUG":
            # Only log debug messages if debug mode is enabled
            if self.debug_mode:
                self.logger.debug(message)
    
    def clear_log_file(self):
        """Clear the log file"""
        for handler in self.logger.handlers:
            if isinstance(handler, logging.FileHandler):
                # Close the file handler to release the file
                handler.close()
                # Truncate the file
                with open(handler.baseFilename, 'w') as f:
                    f.truncate(0)
                # Reopen the handler
                handler.stream = open(handler.baseFilename, handler.mode)
                self.log("Log file cleared", "info")
                break 