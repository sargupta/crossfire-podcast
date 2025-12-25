"""
Tests for Observability Module
Tests logging, tracing, and metrics collection
"""

import sys
import time
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

from observability import (  # noqa: E402
    MetricsCollector,
    Observability,
    SimpleTracer,
    StructuredLogger,
)


class TestStructuredLogger:
    """Test structured logging"""

    def test_logger_initialization(self):
        """Test logger initializes correctly"""
        logger = StructuredLogger("test_logger")
        assert logger.logger.name == "test_logger"
        assert logger.logger.level == 20  # INFO level

    def test_logger_info(self):
        """Test info logging"""
        logger = StructuredLogger("test")
        # Should not raise exception
        logger.info("Test message", extra_field="value")

    def test_logger_error(self):
        """Test error logging"""
        logger = StructuredLogger("test")
        # Should not raise exception
        logger.error("Error message", error_code=500)

    def test_logger_debug(self):
        """Test debug logging"""
        logger = StructuredLogger("test")
        # Should not raise exception
        logger.debug("Debug message", debug_info="test")


class TestSimpleTracer:
    """Test tracing functionality"""

    def test_tracer_initialization(self):
        """Test tracer initializes correctly"""
        tracer = SimpleTracer("test_tracer")
        assert tracer.name == "test_tracer"
        assert tracer.traces == []

    def test_span_basic(self):
        """Test basic span creation"""
        tracer = SimpleTracer()

        with tracer.span("test_operation"):
            time.sleep(0.1)

        assert len(tracer.traces) == 1
        assert tracer.traces[0]["operation"] == "test_operation"
        assert "duration" in tracer.traces[0]
        assert tracer.traces[0]["duration"] >= 0.1

    def test_span_with_attributes(self):
        """Test span with custom attributes"""
        tracer = SimpleTracer()

        with tracer.span("test_op", topic="AI", turns=5):
            pass

        assert len(tracer.traces) == 1
        assert tracer.traces[0]["attributes"]["topic"] == "AI"
        assert tracer.traces[0]["attributes"]["turns"] == 5

    def test_multiple_spans(self):
        """Test multiple spans"""
        tracer = SimpleTracer()

        with tracer.span("operation1"):
            pass

        with tracer.span("operation2"):
            pass

        assert len(tracer.traces) == 2
        assert tracer.traces[0]["operation"] == "operation1"
        assert tracer.traces[1]["operation"] == "operation2"

    def test_nested_spans(self):
        """Test nested spans"""
        tracer = SimpleTracer()

        with tracer.span("outer"):
            with tracer.span("inner"):
                pass

        assert len(tracer.traces) == 2

    def test_get_traces(self):
        """Test getting all traces"""
        tracer = SimpleTracer()

        with tracer.span("test"):
            pass

        traces = tracer.get_traces()
        assert len(traces) == 1
        assert traces[0]["operation"] == "test"


class TestMetricsCollector:
    """Test metrics collection"""

    def test_collector_initialization(self):
        """Test collector initializes correctly"""
        collector = MetricsCollector()
        assert collector.project_id == "aipodcaster-481909"
        assert collector.metrics == []

    def test_collector_custom_project(self):
        """Test collector with custom project ID"""
        collector = MetricsCollector(project_id="custom-project")
        assert collector.project_id == "custom-project"

    def test_record_debate_generated(self):
        """Test recording debate generation metric"""
        collector = MetricsCollector()

        collector.record_debate_generated("Test Topic", 5.5, success=True)

        assert len(collector.metrics) == 1
        metric = collector.metrics[0]
        assert metric["type"] == "debate_generated"
        assert metric["topic"] == "Test Topic"
        assert metric["duration"] == 5.5
        assert metric["success"] is True
        assert "timestamp" in metric

    def test_record_debate_failed(self):
        """Test recording failed debate"""
        collector = MetricsCollector()

        collector.record_debate_generated("Failed Topic", 2.0, success=False)

        metric = collector.metrics[0]
        assert metric["success"] is False

    def test_record_quality_score(self):
        """Test recording quality score"""
        collector = MetricsCollector()

        collector.record_quality_score("coherence", 0.95, speaker="shakti")

        assert len(collector.metrics) == 1
        metric = collector.metrics[0]
        assert metric["type"] == "quality_score"
        assert metric["score_type"] == "coherence"
        assert metric["value"] == 0.95
        assert metric["speaker"] == "shakti"

    def test_record_quality_score_no_speaker(self):
        """Test recording quality score without speaker"""
        collector = MetricsCollector()

        collector.record_quality_score("safety", 0.92)

        metric = collector.metrics[0]
        assert metric["speaker"] is None

    def test_record_turn_generated(self):
        """Test recording turn generation"""
        collector = MetricsCollector()

        collector.record_turn_generated("sovereignist", 3, 1.2)

        assert len(collector.metrics) == 1
        metric = collector.metrics[0]
        assert metric["type"] == "turn_generated"
        assert metric["speaker"] == "sovereignist"
        assert metric["turn_number"] == 3
        assert metric["duration"] == 1.2

    def test_get_metrics_summary_empty(self):
        """Test metrics summary with no metrics"""
        collector = MetricsCollector()

        summary = collector.get_metrics_summary()

        assert summary["total_debates"] == 0
        assert summary["successful_debates"] == 0
        assert summary["total_turns"] == 0
        assert summary["success_rate"] == 0
        assert summary["total_metrics_collected"] == 0

    def test_get_metrics_summary_with_data(self):
        """Test metrics summary with data"""
        collector = MetricsCollector()

        # Add some metrics
        collector.record_debate_generated("Topic 1", 5.0, success=True)
        collector.record_debate_generated("Topic 2", 6.0, success=True)
        collector.record_debate_generated("Topic 3", 4.0, success=False)
        collector.record_turn_generated("agent1", 1, 1.0)
        collector.record_turn_generated("agent2", 2, 1.5)
        collector.record_quality_score("coherence", 0.9)
        collector.record_quality_score("coherence", 0.8)
        collector.record_quality_score("safety", 0.95)

        summary = collector.get_metrics_summary()

        assert summary["total_debates"] == 3
        assert summary["successful_debates"] == 2
        assert summary["total_turns"] == 2
        assert summary["success_rate"] == 2 / 3
        assert summary["total_metrics_collected"] == 8

        # Check average scores
        assert "coherence" in summary["average_quality_scores"]
        # Average of 0.9 and 0.8 is 0.85
        assert abs(summary["average_quality_scores"]["coherence"] - 0.85) < 0.01
        assert abs(summary["average_quality_scores"]["safety"] - 0.95) < 0.01


class TestObservability:
    """Test integrated observability"""

    def test_observability_initialization(self):
        """Test observability initializes all components"""
        obs = Observability()

        assert obs.logger is not None
        assert obs.tracer is not None
        assert obs.metrics is not None

    def test_log_debate_start(self):
        """Test logging debate start"""
        obs = Observability()

        # Should not raise exception
        obs.log_debate_start("Test Topic", 5, "session123")

    def test_log_debate_complete(self):
        """Test logging debate completion"""
        obs = Observability()

        obs.log_debate_complete("Test Topic", "session123", 10.5)

        # Should record metric
        assert len(obs.metrics.metrics) == 1
        metric = obs.metrics.metrics[0]
        assert metric["type"] == "debate_generated"
        assert metric["topic"] == "Test Topic"
        assert metric["duration"] == 10.5
        assert metric["success"] is True

    def test_log_turn_generated(self):
        """Test logging turn generation"""
        obs = Observability()

        # Should not raise exception
        obs.log_turn_generated("shakti", 1, "Test response text")

    def test_log_error(self):
        """Test logging errors"""
        obs = Observability()

        # Should not raise exception
        obs.log_error("TestError", "Something went wrong", context="test")

    def test_integrated_workflow(self):
        """Test complete observability workflow"""
        obs = Observability()

        # Start debate
        obs.log_debate_start("AI Ethics", 4, "debate_456")

        # Trace debate generation
        with obs.tracer.span("debate_generation", topic="AI Ethics"):
            # Generate turns
            for i in range(4):
                with obs.tracer.span("turn_generation", turn=i):
                    obs.log_turn_generated(f"agent_{i}", i, "Response text")
                    obs.metrics.record_turn_generated(f"agent_{i}", i, 0.5)

            # Record quality scores
            obs.metrics.record_quality_score("coherence", 0.92)
            obs.metrics.record_quality_score("safety", 0.95)

        # Complete debate
        obs.log_debate_complete("AI Ethics", "debate_456", 5.0)

        # Verify metrics
        summary = obs.metrics.get_metrics_summary()
        assert summary["total_debates"] == 1
        assert summary["successful_debates"] == 1
        assert summary["total_turns"] == 4
        assert summary["success_rate"] == 1.0

        # Verify traces
        traces = obs.tracer.get_traces()
        assert len(traces) >= 5  # 1 debate + 4 turns


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
