"""acclimatize: check an itinerary for rapid-ascent altitude risks."""

from .core import Report, Stop, Warning, assess_itinerary

__all__ = ["Report", "Stop", "Warning", "assess_itinerary"]
__version__ = "0.1.0"
