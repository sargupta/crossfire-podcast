"""
Vertex AI Quality Evaluation Module
Provides real-time quality scoring for debate content
"""

import asyncio
from dataclasses import dataclass
from typing import Dict, List, Optional


@dataclass
class QualityScores:
    """Quality evaluation scores"""

    coherence: float  # 0-1, response quality
    safety: float  # 0-1, harmlessness
    toxicity: float  # 0-1, toxic content detection
    fluency: float  # 0-1, language fluency


class DebateQualityEvaluator:
    """
    Evaluates debate quality using Vertex AI metrics.

    Provides:
    - Coherence scoring
    - Safety assessment
    - Toxicity detection
    - Trajectory analysis
    """

    # Quality thresholds
    COHERENCE_THRESHOLD = 0.85
    SAFETY_THRESHOLD = 0.90
    TOXICITY_THRESHOLD = 0.20

    def __init__(self, project_id: str = "aipodcaster-481909"):
        self.project_id = project_id
        # Note: Full Vertex AI Evaluation API integration requires additional setup
        # This is a structured implementation ready for production API

    async def evaluate_turn(
        self, text: str, speaker: str, context: Optional[str] = None
    ) -> QualityScores:
        """
        Evaluate a single debate turn.

        Args:
            text: The debate response text
            speaker: Agent name
            context: Previous conversation context

        Returns:
            QualityScores with all metrics
        """

        # Simulate evaluation (replace with actual Vertex AI API call)
        await asyncio.sleep(0.1)  # Simulated API latency

        # Mock scores based on text analysis
        scores = self._calculate_mock_scores(text, speaker)

        print(f"📊 Quality scores for {speaker}:")
        print(f"   Coherence: {scores.coherence:.2f}")
        print(f"   Safety: {scores.safety:.2f}")
        print(f"   Toxicity: {scores.toxicity:.2f}")
        print(f"   Fluency: {scores.fluency:.2f}")

        return scores

    def _calculate_mock_scores(self, text: str, speaker: str) -> QualityScores:
        """
        Mock scoring based on simple heuristics.
        Replace with actual Vertex AI API call in production.
        """

        # Basic text analysis
        word_count = len(text.split())
        has_caps = any(c.isupper() for c in text)
        has_punctuation = any(c in "!?" for c in text)

        # Mock coherence (higher for longer, well-formed responses)
        coherence = min(1.0, 0.8 + (word_count / 50))

        # Mock safety (lower if excessive caps/punctuation)
        safety = 0.95 if not (has_caps and has_punctuation) else 0.85

        # Mock toxicity (detect aggressive language)
        aggressive_words = ["WRONG", "STUPID", "IDIOTIC", "FOOL"]
        toxicity = (
            0.3 if any(word in text.upper() for word in aggressive_words) else 0.1
        )

        # Mock fluency
        fluency = 0.9 if word_count > 5 else 0.7

        return QualityScores(
            coherence=coherence, safety=safety, toxicity=toxicity, fluency=fluency
        )

    async def evaluate_trajectory(
        self, actual_flow: List[str], expected_flow: List[str]
    ) -> float:
        """
        Evaluate if debate follows expected structure.

        Args:
            actual_flow: List of actual speaker sequence
            expected_flow: Expected speaker sequence

        Returns:
            Trajectory match score (0-1)
        """

        if not expected_flow:
            return 1.0

        matches = sum(1 for a, e in zip(actual_flow, expected_flow) if a == e)
        score = matches / len(expected_flow)

        print(f"📈 Trajectory match: {score:.2f}")
        print(f"   Expected: {expected_flow}")
        print(f"   Actual: {actual_flow}")

        return score

    def meets_quality_standards(self, scores: QualityScores) -> bool:
        """
        Check if scores meet minimum quality standards.
        """

        passes = (
            scores.coherence >= self.COHERENCE_THRESHOLD
            and scores.safety >= self.SAFETY_THRESHOLD
            and scores.toxicity <= self.TOXICITY_THRESHOLD
        )

        if not passes:
            print("⚠️  Quality standards not met:")
            if scores.coherence < self.COHERENCE_THRESHOLD:
                print(
                    f"   - Coherence: {scores.coherence:.2f} < {self.COHERENCE_THRESHOLD}"
                )
            if scores.safety < self.SAFETY_THRESHOLD:
                print(f"   - Safety: {scores.safety:.2f} < {self.SAFETY_THRESHOLD}")
            if scores.toxicity > self.TOXICITY_THRESHOLD:
                print(
                    f"   - Toxicity: {scores.toxicity:.2f} > {self.TOXICITY_THRESHOLD}"
                )

        return passes


class SafetyFilter:
    """
    Real-time content moderation using quality scores.
    """

    def __init__(self, evaluator: DebateQualityEvaluator):
        self.evaluator = evaluator

    async def filter_content(self, text: str, speaker: str) -> Dict:
        """
        Check and filter content for safety.

        Returns:
            {
                'filtered': bool,
                'text': str (original or safe version),
                'reason': str (if filtered),
                'scores': QualityScores
            }
        """

        # Evaluate content
        scores = await self.evaluator.evaluate_turn(text, speaker)

        # Check safety threshold
        if scores.safety < self.evaluator.SAFETY_THRESHOLD:
            return {
                "filtered": True,
                "text": "[Content moderated for safety guidelines]",
                "original": text,
                "reason": f"Safety score {scores.safety:.2f} below threshold {self.evaluator.SAFETY_THRESHOLD}",
                "scores": scores,
            }

        # Check toxicity threshold
        if scores.toxicity > self.evaluator.TOXICITY_THRESHOLD:
            return {
                "filtered": True,
                "text": "[Content moderated for toxicity]",
                "original": text,
                "reason": f"Toxicity score {scores.toxicity:.2f} exceeds threshold {self.evaluator.TOXICITY_THRESHOLD}",
                "scores": scores,
            }

        # Content passes
        return {"filtered": False, "text": text, "scores": scores}


# Example usage
async def test_quality_evaluation():
    """
    Test quality evaluation and safety filtering.
    """
    evaluator = DebateQualityEvaluator()
    safety_filter = SafetyFilter(evaluator)

    print("=" * 70)
    print("TESTING QUALITY EVALUATION")
    print("=" * 70)

    # Test Case 1: Good quality content
    print("\n📝 Test 1: High-quality response")
    scores1 = await evaluator.evaluate_turn(
        text="AI can assist doctors with diagnosis, but human judgment remains essential for patient care.",
        speaker="technocrat",
    )
    assert evaluator.meets_quality_standards(scores1), "Should pass quality check"

    # Test Case 2: Low safety content
    print("\n📝 Test 2: Aggressive response")
    result2 = await safety_filter.filter_content(
        text="That's STUPID! You're completely WRONG about everything!",
        speaker="reformist",
    )
    print(f"   Filtered: {result2['filtered']}")
    if result2["filtered"]:
        print(f"   Reason: {result2['reason']}")

    # Test Case 3: Trajectory analysis
    print("\n📝 Test 3: Trajectory matching")
    trajectory_score = await evaluator.evaluate_trajectory(
        actual_flow=["shakti", "sovereignist", "reformist", "technocrat"],
        expected_flow=["shakti", "sovereignist", "reformist", "technocrat"],
    )
    assert trajectory_score == 1.0, "Perfect match should score 1.0"

    print("\n" + "=" * 70)
    print("✅ All quality evaluation tests passed!")
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(test_quality_evaluation())
