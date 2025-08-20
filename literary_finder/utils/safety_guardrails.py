"""Safety guardrails for content protection and validation."""

import re
import logging
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class SafetyViolation:
    """Represents a safety violation detected in content."""
    severity: str  # "low", "medium", "high", "critical"
    category: str  # "inappropriate_content", "personal_info", "misinformation", etc.
    description: str
    location: str  # Where in the content the violation was found
    suggested_action: str


class ContentSafetyGuard:
    """Content safety validation and filtering system."""
    
    def __init__(self):
        # Patterns for detecting potentially problematic content
        self.inappropriate_patterns = [
            r'\b(?:hate|violent|explicit|offensive)\b',
            r'\b(?:discriminat|racist|sexist)\w*\b',
        ]
        
        # Patterns for detecting personal information
        self.pii_patterns = [
            r'\b\d{3}-\d{2}-\d{4}\b',  # SSN pattern
            r'\b\d{3}\.\d{2}\.\d{4}\b',  # SSN pattern
            r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',  # Email
            r'\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b',  # Credit card pattern
            r'\b\(\d{3}\)\s?\d{3}-?\d{4}\b',  # Phone number
        ]
        
        # Patterns for detecting potential misinformation indicators
        self.misinformation_patterns = [
            r'\b(?:secret|conspiracy|cover-?up|hidden truth)\b',
            r'\b(?:they don\'t want you to know|suppressed|censored)\b',
        ]
        
        # Safe content indicators (literary analysis terms)
        self.literary_safe_patterns = [
            r'\b(?:literary|analysis|criticism|scholarly|academic)\b',
            r'\b(?:theme|style|narrative|character|plot)\b',
            r'\b(?:author|writer|poet|novelist|bibliography)\b',
            r'\b(?:published|publication|book|novel|story)\b',
        ]

    def validate_content(self, content: str, content_type: str = "general") -> Tuple[bool, List[SafetyViolation]]:
        """
        Validate content for safety issues.
        
        Args:
            content: Content to validate
            content_type: Type of content ("biography", "analysis", "bibliography", etc.)
            
        Returns:
            Tuple of (is_safe, list_of_violations)
        """
        violations = []
        
        # Check for inappropriate content
        violations.extend(self._check_inappropriate_content(content))
        
        # Check for personal information
        violations.extend(self._check_personal_information(content))
        
        # Check for potential misinformation indicators
        violations.extend(self._check_misinformation_indicators(content))
        
        # Check content quality for literary analysis
        if content_type in ["biography", "analysis", "bibliography"]:
            violations.extend(self._check_literary_content_quality(content))
        
        # Determine if content is safe
        critical_violations = [v for v in violations if v.severity == "critical"]
        high_violations = [v for v in violations if v.severity == "high"]
        
        is_safe = len(critical_violations) == 0 and len(high_violations) <= 1
        
        if violations:
            logger.warning(f"Content safety check found {len(violations)} violations")
            for violation in violations:
                logger.warning(f"  {violation.severity.upper()}: {violation.description}")
        
        return is_safe, violations

    def sanitize_content(self, content: str, violations: List[SafetyViolation]) -> str:
        """
        Sanitize content by removing or redacting problematic parts.
        
        Args:
            content: Original content
            violations: List of violations found
            
        Returns:
            Sanitized content
        """
        sanitized = content
        
        for violation in violations:
            if violation.category == "personal_info":
                # Redact personal information
                for pattern in self.pii_patterns:
                    sanitized = re.sub(pattern, "[REDACTED]", sanitized)
            
            elif violation.category == "inappropriate_content":
                # Remove inappropriate content sections
                if violation.severity in ["high", "critical"]:
                    sanitized = sanitized.replace(violation.location, "[CONTENT REMOVED FOR SAFETY]")
        
        return sanitized

    def _check_inappropriate_content(self, content: str) -> List[SafetyViolation]:
        """Check for inappropriate content patterns."""
        violations = []
        
        for pattern in self.inappropriate_patterns:
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                violations.append(SafetyViolation(
                    severity="medium",
                    category="inappropriate_content",
                    description=f"Potentially inappropriate content detected: '{match.group()}'",
                    location=match.group(),
                    suggested_action="Review and potentially remove"
                ))
        
        return violations

    def _check_personal_information(self, content: str) -> List[SafetyViolation]:
        """Check for personal information patterns."""
        violations = []
        
        for pattern in self.pii_patterns:
            matches = re.finditer(pattern, content)
            for match in matches:
                violations.append(SafetyViolation(
                    severity="high",
                    category="personal_info",
                    description=f"Personal information detected: {match.group()[:3]}...",
                    location=match.group(),
                    suggested_action="Redact or remove personal information"
                ))
        
        return violations

    def _check_misinformation_indicators(self, content: str) -> List[SafetyViolation]:
        """Check for potential misinformation indicators."""
        violations = []
        
        for pattern in self.misinformation_patterns:
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                violations.append(SafetyViolation(
                    severity="medium",
                    category="misinformation",
                    description=f"Potential misinformation indicator: '{match.group()}'",
                    location=match.group(),
                    suggested_action="Verify factual accuracy and sources"
                ))
        
        return violations

    def _check_literary_content_quality(self, content: str) -> List[SafetyViolation]:
        """Check quality indicators for literary content."""
        violations = []
        
        # Check if content contains appropriate literary terminology
        literary_matches = 0
        for pattern in self.literary_safe_patterns:
            literary_matches += len(re.findall(pattern, content, re.IGNORECASE))
        
        # If content is very short and lacks literary context
        if len(content.strip()) < 100:
            violations.append(SafetyViolation(
                severity="low",
                category="content_quality",
                description="Content appears too brief for meaningful literary analysis",
                location="entire_content",
                suggested_action="Consider requesting more detailed information"
            ))
        
        # If content lacks literary terminology
        elif literary_matches < 2 and len(content) > 500:
            violations.append(SafetyViolation(
                severity="low",
                category="content_quality",
                description="Content may not be relevant to literary analysis",
                location="entire_content",
                suggested_action="Verify content relevance to literary research"
            ))
        
        return violations

    def validate_author_name(self, author_name: str) -> Tuple[bool, Optional[str]]:
        """
        Validate that an author name is appropriate for literary research.
        
        Args:
            author_name: Name to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not author_name or not author_name.strip():
            return False, "Author name cannot be empty"
        
        # Remove extra whitespace
        clean_name = re.sub(r'\s+', ' ', author_name.strip())
        
        # Check for reasonable length
        if len(clean_name) < 2:
            return False, "Author name too short"
        
        if len(clean_name) > 100:
            return False, "Author name too long"
        
        # Check for basic name pattern (letters, spaces, common punctuation)
        if not re.match(r'^[A-Za-z\s\.\-\']+$', clean_name):
            return False, "Author name contains invalid characters"
        
        # Check for obvious test/inappropriate inputs
        inappropriate_names = [
            'test', 'testing', 'admin', 'null', 'undefined',
            'fuck', 'shit', 'damn', 'hell'
        ]
        
        if clean_name.lower() in inappropriate_names:
            return False, "Invalid author name"
        
        return True, None

    def create_safety_report(self, violations: List[SafetyViolation]) -> Dict[str, Any]:
        """Create a comprehensive safety report."""
        if not violations:
            return {
                "status": "safe",
                "total_violations": 0,
                "severity_breakdown": {},
                "recommendations": ["Content passed all safety checks"]
            }
        
        severity_counts = {}
        categories = set()
        recommendations = []
        
        for violation in violations:
            severity_counts[violation.severity] = severity_counts.get(violation.severity, 0) + 1
            categories.add(violation.category)
            if violation.suggested_action not in recommendations:
                recommendations.append(violation.suggested_action)
        
        # Determine overall status
        if any(v.severity == "critical" for v in violations):
            status = "unsafe"
        elif any(v.severity == "high" for v in violations):
            status = "needs_review"
        else:
            status = "safe_with_warnings"
        
        return {
            "status": status,
            "total_violations": len(violations),
            "severity_breakdown": severity_counts,
            "categories_affected": list(categories),
            "recommendations": recommendations,
            "detailed_violations": [
                {
                    "severity": v.severity,
                    "category": v.category,
                    "description": v.description,
                    "suggested_action": v.suggested_action
                }
                for v in violations
            ]
        }