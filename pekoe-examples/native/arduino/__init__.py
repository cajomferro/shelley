from unittest.mock import MagicMock

Arduino = MagicMock()
Arduino.pinMode = MagicMock()
Arduino.attachInterruptOnce = MagicMock()
Arduino.digitalWrite = MagicMock()
Arduino.INPUT = MagicMock()
Arduino.OUTPUT = MagicMock()
Arduino.LOW = MagicMock()
Arduino.HIGH = MagicMock()
Arduino.FALL = MagicMock()
Arduino.RISE = MagicMock()
Arduino.TIMEOUT = MagicMock()
