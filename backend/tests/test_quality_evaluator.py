"""
Tests for Quality Evaluator
Tests quality scoring, safety filtering, and trajectory analysis
"""

import pytest
import asyncio
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from quality_evaluator import (  # noqa: E402
    DebateQualityEvaluator,
    SafetyFilter,
    QualityScores,
)


class TestQualityScores:
    """Test the QualityScores dataclass"""

    def test_quality_scores_creation(self):
        """Test creating quality scores"""
        scores = QualityScores(
            coherence=0.95, safety=0.92, toxicity=0.10, fluency=0.90
        )

        assert scores.coherence == 0.95
        assert scores.safety == 0.92
        assert scores.toxicity == 0.10
        assert scores.fluency == 0.90


class TestDebateQualityEvaluator:
    """Test the quality evaluator"""

    def test_evaluator_initialization(self):
        """Test evaluator initializes correctly"""
        evaluator = DebateQualityEvaluator()
        assert evaluator.project_id == "aipodcaster-481909"
        assert evaluator.COHERENCE_THRESHOLD == 0.85
        assert evaluator.SAFETY_THRESHOLD == 0.90
        assert evaluator.TOXICITY_THRESHOLD == 0.20

    def test_evaluator_custom_project(self):
        """Test evaluator with custom project ID"""
        evaluator = DebateQualityEvaluator(project_id="custom-project")
        assert evaluator.project_id == "custom-project"

    @pytest.mark.asyncio
    async def test_evaluate_turn_basic(self):
        """Test basic turn evaluation"""
        evaluator = DebateQualityEvaluator()

        scores = await evaluator.evaluate_turn(
            text="This is a well-reasoned argument about AI.",
            speaker="technocrat",
        )

        assert isinstance(scores, QualityScores)
        assert 0 <= scores.coherence <= 1
        assert 0 <= scores.safety <= 1
        assert 0 <= scores.toxicity <= 1
        assert 0 <= scores.fluency <= 1

    @pytest.mark.asyncio
    async def test_evaluate_turn_with_context(self):
        """Test turn evaluation with context"""
        evaluator = DebateQualityEvaluator()

        scores = await evaluator.evaluate_turn(
            text="I agree with the previous point.",
            speaker="humanist",
            context="Previous speaker made a good argument.",
        )

        assert isinstance(scores, QualityScores)

    def test_calculate_mock_scores_short_text(self):
        """Test mock scoring for short text"""
        evaluator = DebateQualityEvaluator()

        scores = evaluator._calculate_mock_scores("Short", "speaker")

        assert scores.coherence > 0
        assert scores.safety > 0
        assert scores.fluency > 0

    def test_calculate_mock_scores_long_text(self):
        """Test mock scoring for longer text"""
        evaluator = DebateQualityEvaluator()

        long_text = " ".join(["word"] * 50)
        scores = evaluator._calculate_mock_scores(long_text, "speaker")

        # Longer text should have higher coherence
        assert scores.coherence >= 0.8

    def test_calculate_mock_scores_aggressive_text(self):
        """Test mock scoring for aggressive text"""
        evaluator = DebateQualityEvaluator()

        scores = evaluator._calculate_mock_scores(
            "That's WRONG and STUPID!", "speaker"
        )

        # Aggressive text should have higher toxicity
        assert scores.toxicity > 0.2

    def test_calculate_mock_scores_caps_and_punctuation(self):
        """Test scoring with caps and punctuation"""
        evaluator = DebateQualityEvaluator()

        scores = evaluator._calculate_mock_scores("THIS IS LOUD!?", "speaker")

        # Caps and punctuation should lower safety
        assert scores.safety < 0.95

    @pytest.mark.asyncio
    async def test_evaluate_trajectory_perfect_match(self):
        """Test trajectory evaluation with perfect match"""
        evaluator = DebateQualityEvaluator()

        score = await evaluator.evaluate_trajectory(
            actual_flow=["shakti", "sovereignist", "reformist"],
            expected_flow=["shakti", "sovereignist", "reformist"],
        )

        assert score == 1.0

    @pytest.mark.asyncio
    async def test_evaluate_trajectory_partial_match(self):
        """Test trajectory evaluation with partial match"""
        evaluator = DebateQualityEvaluator()

        score = await evaluator.evaluate_trajectory(
            actual_flow=["shakti", "reformist", "technocrat"],
            expected_flow=["shakti", "sovereignist", "reformist"],
        )

        # 1 out of 3 matches
        assert 0 < score < 1

    @pytest.mark.asyncio
    async def test_evaluate_trajectory_no_match(self):
        """Test trajectory evaluation with no match"""
        evaluator = DebateQualityEvaluator()

        score = await evaluator.evaluate_trajectory(
            actual_flow=["humanist", "technocrat", "reformist"],
            expected_flow=["shakti", "sovereignist", "humanist"],
        )

        assert 0 <= score < 1

    @pytest.mark.asyncio
    async def test_evaluate_trajectory_empty_expected(self):
        """Test trajectory evaluation with empty expected flow"""
        evaluator = DebateQualityEvaluator()

        score = await evaluator.evaluate_trajectory(
            actual_flow=["shakti", "sovereignist"], expected_flow=[]
        )

        assert score == 1.0

    def test_meets_quality_standards_pass(self):
        """Test quality standards check - passing"""
        evaluator = DebateQualityEvaluator()

        scores = QualityScores(
            coherence=0.95, safety=0.95, toxicity=0.10, fluency=0.90
        )

        assert evaluator.meets_quality_standards(scores) is True

    def test_meets_quality_standards_fail_coherence(self):
        """Test quality standards check - failing coherence"""
        evaluator = DebateQualityEvaluator()

        scores = QualityScores(
            coherence=0.70, safety=0.95, toxicity=0.10, fluency=0.90
        )

        assert evaluator.meets_quality_standards(scores) is False

    def test_meets_quality_standards_fail_safety(self):
        """Test quality standards check - failing safety"""
        evaluator = DebateQualityEvaluator()

        scores = QualityScores(
            coherence=0.95, safety=0.80, toxicity=0.10, fluency=0.90
        )

        assert evaluator.meets_quality_standards(scores) is False

    def test_meets_quality_standards_fail_toxicity(self):
        """Test quality standards check - failing toxicity"""
        evaluator = DebateQualityEvaluator()

        scores = QualityScores(
            coherence=0.95, safety=0.95, toxicity=0.30, fluency=0.90
        )

        assert evaluator.meets_quality_standards(scores) is False

    def test_meets_quality_standards_multiple_failures(self):
        """Test quality standards check - multiple failures"""
        evaluator = DebateQualityEvaluator()

        scores = QualityScores(
            coherence=0.70, safety=0.80, toxicity=0.30, fluency=0.90
        )

        assert evaluator.meets_quality_standards(scores) is False


class TestSafetyFilter:
    """Test the safety filter"""

    def test_safety_filter_initialization(self):
        """Test safety filter initializes correctly"""
        evaluator = DebateQualityEvaluator()
        safety_filter = SafetyFilter(evaluator)

        assert safety_filter.evaluator == evaluator

    @pytest.mark.asyncio
    async def test_filter_content_safe(self):
        """Test filtering safe content"""
        evaluator = DebateQualityEvaluator()
        safety_filter = SafetyFilter(evaluator)

        result = await safety_filter.filter_content(
            text="This is a reasonable argument.", speaker="technocrat"
        )

        assert result["filtered"] is False
        assert result["text"] == "This is a reasonable argument."
        assert "scores" in result

    @pytest.mark.asyncio
    async def test_filter_content_toxic(self):
        """Test filtering toxic content"""
        evaluator = DebateQualityEvaluator()
        safety_filter = SafetyFilter(evaluator)

        result = await safety_filter.filter_content(
            text="That's STUPID and IDIOTIC!", speaker="reformist"
        )

        # Should be filtered (either for safety or toxicity)
        assert result["filtered"] is True
        assert result["text"] in [
            "[Content moderated for toxicity]",
            "[Content moderated for safety guidelines]",
        ]
        assert "original" in result
        assert "reason" in result
        assert "scores" in result

    @pytest.mark.asyncio
    async def test_filter_content_unsafe(self):
        """Test filtering unsafe content"""
        evaluator = DebateQualityEvaluator()
        safety_filter = SafetyFilter(evaluator)

        # Create text that will trigger low safety score
        result = await safety_filter.filter_content(
            text="DANGEROUS!!! HARMFUL!!! WRONG!!!", speaker="speaker"
        )

        # Should be filtered for either safety or toxicity
        assert result["filtered"] is True
        assert "reason" in result

    @pytest.mark.asyncio
    async def test_filter_content_preserves_scores(self):
        """Test that filtering preserves quality scores"""
        evaluator = DebateQualityEvaluator()
        safety_filter = SafetyFilter(evaluator)

        result = await safety_filter.filter_content(
            text="Normal text", speaker="speaker"
        )

        assert "scores" in result
        assert isinstance(result["scores"], QualityScores)


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
