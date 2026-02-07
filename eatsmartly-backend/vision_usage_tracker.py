"""
Vision API Usage Tracker - Enforces free tier limit of 1000 units/month.

Unit Calculation:
- DOCUMENT_TEXT_DETECTION = 1 unit per image
- TEXT_DETECTION = 1 unit per image
- Each feature × each image = 1 unit

Monthly free tier: 1000 units per feature
This tracker enforces a conservative limit across all features.
"""
import json
import os
from datetime import datetime, timedelta
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

USAGE_FILE = os.path.join(os.path.dirname(__file__), 'vision_usage.json')
MONTHLY_LIMIT = 1000  # Free tier limit
WARNING_THRESHOLD = 0.7  # Alert at 70% usage (700 units)
CRITICAL_THRESHOLD = 0.95  # Stop at 95% usage


class VisionUsageTracker:
    """Tracks Google Vision API usage to enforce free tier limits."""
    
    def __init__(self, limit: int = MONTHLY_LIMIT):
        self.limit = limit
        self.usage_data = self._load_usage()
        
    def _load_usage(self) -> Dict[str, Any]:
        """Load usage data from file."""
        if os.path.exists(USAGE_FILE):
            try:
                with open(USAGE_FILE, 'r') as f:
                    data = json.load(f)
                    # Reset if month changed
                    last_reset = datetime.fromisoformat(data.get('last_reset', '2000-01-01'))
                    now = datetime.utcnow()
                    if now.month != last_reset.month or now.year != last_reset.year:
                        logger.info(f"New month detected, resetting usage counter from {data.get('units_used', 0)}")
                        return self._init_usage()
                    return data
            except Exception as e:
                logger.warning(f"Failed to load usage data: {e}, initializing fresh")
                return self._init_usage()
        return self._init_usage()
    
    def _init_usage(self) -> Dict[str, Any]:
        """Initialize usage data structure."""
        return {
            'units_used': 0,
            'requests_count': 0,
            'last_reset': datetime.utcnow().isoformat(),
            'last_request': None,
            'monthly_limit': self.limit
        }
    
    def _save_usage(self):
        """Save usage data to file."""
        try:
            with open(USAGE_FILE, 'w') as f:
                json.dump(self.usage_data, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save usage data: {e}")
    
    def can_make_request(self, units_needed: int = 1) -> tuple[bool, str]:
        """
        Check if request can be made without exceeding limit.
        
        Returns:
            (can_proceed, message)
        """
        current = self.usage_data['units_used']
        new_total = current + units_needed
        
        # Hard stop at 95% to leave buffer
        if new_total >= self.limit * CRITICAL_THRESHOLD:
            remaining = self.limit - current
            return False, (
                f"Vision API monthly limit reached: {current}/{self.limit} units used. "
                f"Only {remaining} units remaining. Resets next month. "
                f"Using OCR.space fallback."
            )
        
        # Warning at 70%
        if new_total >= self.limit * WARNING_THRESHOLD and current < self.limit * WARNING_THRESHOLD:
            logger.warning(
                f"⚠️ Vision API usage at {(new_total/self.limit)*100:.1f}%: "
                f"{new_total}/{self.limit} units used. Consider monitoring closely."
            )
        
        return True, ""
    
    def record_request(self, units: int = 1, success: bool = True):
        """Record a Vision API request."""
        if success:
            self.usage_data['units_used'] += units
            self.usage_data['requests_count'] += 1
            self.usage_data['last_request'] = datetime.utcnow().isoformat()
            self._save_usage()
            
            percent = (self.usage_data['units_used'] / self.limit) * 100
            logger.info(
                f"📊 Vision API usage: {self.usage_data['units_used']}/{self.limit} units "
                f"({percent:.1f}%) | Requests: {self.usage_data['requests_count']}"
            )
    
    def get_usage_stats(self) -> Dict[str, Any]:
        """Get current usage statistics."""
        current = self.usage_data['units_used']
        percent = (current / self.limit) * 100
        remaining = self.limit - current
        
        return {
            'units_used': current,
            'units_limit': self.limit,
            'units_remaining': remaining,
            'percentage_used': round(percent, 1),
            'requests_count': self.usage_data['requests_count'],
            'last_reset': self.usage_data['last_reset'],
            'last_request': self.usage_data['last_request'],
            'status': 'ok' if percent < 70 else 'warning' if percent < 95 else 'critical'
        }
    
    def reset_usage(self):
        """Manually reset usage (for testing or new month)."""
        logger.info("Manually resetting Vision API usage tracker")
        self.usage_data = self._init_usage()
        self._save_usage()


# Global tracker instance
_tracker = None

def get_usage_tracker() -> VisionUsageTracker:
    """Get or create the global usage tracker."""
    global _tracker
    if _tracker is None:
        _tracker = VisionUsageTracker()
    return _tracker
