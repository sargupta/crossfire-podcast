"""
Observability Module for CROSSFIRE
Implements Cloud Trace, Cloud Monitoring, and Cloud Logging
"""

import logging
import time
from typing import Dict, Optional
from contextlib import contextmanager
from datetime import datetime

# Configure Cloud Logging (structured logging)
class StructuredLogger:
    """
    Structured logging for Cloud Logging integration.
    """
    
    def __init__(self, name: str = 'crossfire'):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.INFO)
        
        # Console handler for development
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
    
    def info(self, message: str, **kwargs):
        """Log info with structured data"""
        self.logger.info(message, extra=kwargs)
    
    def error(self, message: str, **kwargs):
        """Log error with structured data"""
        self.logger.error(message, extra=kwargs, exc_info=True)
    
    def debug(self, message: str, **kwargs):
        """Log debug with structured data"""
        self.logger.debug(message, extra=kwargs)


# Simple trace context for development
class SimpleTracer:
    """
    Simplified tracing for development.
    Production will use Cloud Trace.
    """
    
    def __init__(self, name: str = 'crossfire'):
        self.name = name
        self.traces = []
    
    @contextmanager
    def span(self, operation: str, **attributes):
        """
        Create a trace span.
        
        Usage:
            with tracer.span("debate_generation", topic="AI"):
                # do work
        """
        start_time = time.time()
        span_data = {
            'operation': operation,
            'start_time': start_time,
            'attributes': attributes
        }
        
        print(f"🔍 TRACE START: {operation} {attributes}")
        
        try:
            yield span_data
            
        finally:
            duration = time.time() - start_time
            span_data['duration'] = duration
            span_data['end_time'] = time.time()
            
            self.traces.append(span_data)
            
            print(f"🔍 TRACE END: {operation} ({duration:.2f}s)")
    
    def get_traces(self):
        """Get all traces"""
        return self.traces


# Metrics collector for development
class MetricsCollector:
    """
    Collects custom metrics for Cloud Monitoring.
    """
    
    def __init__(self, project_id: str = 'aipodcaster-481909'):
        self.project_id = project_id
        self.metrics = []
    
    def record_debate_generated(self, topic: str, duration: float, success: bool = True):
        """
        Record debate generation metric.
        """
        metric = {
            'type': 'debate_generated',
            'topic': topic,
            'duration': duration,
            'success': success,
            'timestamp': datetime.now().isoformat()
        }
        
        self.metrics.append(metric)
        
        print(f"📊 METRIC: Debate generated - {topic} ({duration:.2f}s) - {'✅' if success else '❌'}")
    
    def record_quality_score(self, score_type: str, value: float, speaker: str = None):
        """
        Record quality evaluation score.
        """
        metric = {
            'type': 'quality_score',
            'score_type': score_type,
            'value': value,
            'speaker': speaker,
            'timestamp': datetime.now().isoformat()
        }
        
        self.metrics.append(metric)
        
        print(f"📊 METRIC: {score_type} = {value:.2f} (speaker: {speaker})")
    
    def record_turn_generated(self, speaker: str, turn_number: int, duration: float):
        """
        Record individual turn generation.
        """
        metric = {
            'type': 'turn_generated',
            'speaker': speaker,
            'turn_number': turn_number,
            'duration': duration,
            'timestamp': datetime.now().isoformat()
        }
        
        self.metrics.append(metric)
        
        print(f"📊 METRIC: Turn {turn_number} by {speaker} ({duration:.2f}s)")
    
    def get_metrics_summary(self) -> Dict:
        """
        Get summary of collected metrics.
        """
        total_debates = sum(1 for m in self.metrics if m['type'] == 'debate_generated')
        successful_debates = sum(1 for m in self.metrics if m['type'] == 'debate_generated' and m['success'])
        total_turns = sum(1 for m in self.metrics if m['type'] == 'turn_generated')
        
        quality_scores = [m for m in self.metrics if m['type'] == 'quality_score']
        avg_scores = {}
        for score_type in set(m['score_type'] for m in quality_scores):
            scores = [m['value'] for m in quality_scores if m['score_type'] == score_type]
            avg_scores[score_type] = sum(scores) / len(scores) if scores else 0
        
        return {
            'total_debates': total_debates,
            'successful_debates': successful_debates,
            'total_turns': total_turns,
            'success_rate': successful_debates / total_debates if total_debates > 0 else 0,
            'average_quality_scores': avg_scores,
            'total_metrics_collected': len(self.metrics)
        }


# Integrated observability class
class Observability:
    """
    Complete observability for CROSSFIRE debates.
    """
    
    def __init__(self):
        self.logger = StructuredLogger('crossfire')
        self.tracer = SimpleTracer('crossfire')
        self.metrics = MetricsCollector()
    
    def log_debate_start(self, topic: str, turns: int, session_id: str):
        """Log debate start"""
        self.logger.info('Debate started', extra={
            'topic': topic,
            'turns': turns,
            'session_id': session_id
        })
    
    def log_debate_complete(self, topic: str, session_id: str, duration: float):
        """Log debate completion"""
        self.logger.info('Debate completed', extra={
            'topic': topic,
            'session_id': session_id,
            'duration': duration
        })
        
        self.metrics.record_debate_generated(topic, duration, success=True)
    
    def log_turn_generated(self, speaker: str, turn: int, text: str):
        """Log individual turn"""
        self.logger.debug('Turn generated', extra={
            'speaker': speaker,
            'turn': turn,
            'text_length': len(text)
        })
    
    def log_error(self, error_type: str, message: str, **context):
        """Log error with context"""
        self.logger.error(f'{error_type}: {message}', **context)


# Example usage
def test_observability():
    """
    Test observability features.
    """
    obs = Observability()
    
    print("=" * 70)
    print("TESTING OBSERVABILITY")
    print("=" * 70)
    
    # Log debate start
    obs.log_debate_start(
        topic="AI vs Human Intelligence",
        turns=6,
        session_id="debate_test123"
    )
    
    # Trace debate generation
    with obs.tracer.span("debate_generation", topic="AI vs Human Intelligence"):
        time.sleep(0.5)  # Simulate work
        
        # Trace individual turns
        for i in range(3):
            with obs.tracer.span("turn_generation", turn=i, speaker="agent_" + str(i)):
                time.sleep(0.2)
                obs.metrics.record_turn_generated(f"agent_{i}", i, 0.2)
    
    # Record quality scores
    obs.metrics.record_quality_score("coherence", 0.92, speaker="shakti")
    obs.metrics.record_quality_score("safety", 0.95, speaker="shakti")
    obs.metrics.record_quality_score("toxicity", 0.15, speaker="shakti")
    
    # Log completion
    obs.log_debate_complete(
        topic="AI vs Human Intelligence",
        session_id="debate_test123",
        duration=1.5
    )
    
    # Get metrics summary
    summary = obs.metrics.get_metrics_summary()
    
    print("\n" + "=" * 70)
    print("METRICS SUMMARY")
    print("=" * 70)
    print(f"Total Debates: {summary['total_debates']}")
    print(f"Successful: {summary['successful_debates']}")
    print(f"Success Rate: {summary['success_rate']:.1%}")
    print(f"Total Turns: {summary['total_turns']}")
    print(f"Average Scores: {summary['average_quality_scores']}")
    print(f"Total Metrics: {summary['total_metrics_collected']}")
    print("=" * 70)
    
    print("\n✅ Observability test complete!")


if __name__ == "__main__":
    test_observability()
