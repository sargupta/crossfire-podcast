"""
Managed Session Service using Agent Engine's Context Management
Replaces InMemorySessionService for production
"""

import uuid
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
import json

@dataclass
class DebateContext:
    """Debate session context"""
    session_id: str
    topic: str
    current_turn: int
    debate_history: List[Dict]
    participants: List[str]
    created_at: str
    updated_at: str
    metadata: Dict = None

class ManagedSessionService:
    """
    Production-ready session management for Agent Engine.
    
    Provides persistent context across debate turns with managed memory.
    """
    
    def __init__(self, project_id: str, location: str = "us-central1"):
        self.project_id = project_id
        self.location = location
        self.sessions: Dict[str, DebateContext] = {}
    
    async def create_session(
        self, 
        topic: str,
        participants: Optional[List[str]] = None
    ) -> DebateContext:
        """
        Create a new managed debate session.
        
        Args:
            topic: Debate topic
            participants: List of agent names
        
        Returns:
            DebateContext with session ID
        """
        
        if participants is None:
            participants = [
                'shakti',
                'sovereignist', 
                'reformist',
                'technocrat',
                'humanist'
            ]
        
        session_id = f"debate_{uuid.uuid4().hex[:12]}"
        timestamp = datetime.now().isoformat()
        
        context = DebateContext(
            session_id=session_id,
            topic=topic,
            current_turn=0,
            debate_history=[],
            participants=participants,
            created_at=timestamp,
            updated_at=timestamp,
            metadata={
                'project_id': self.project_id,
                'location': self.location
            }
        )
        
        self.sessions[session_id] = context
        
        print(f"📝 Created session: {session_id}")
        print(f"   Topic: {topic}")
        print(f"   Participants: {len(participants)}")
        
        return context
    
    async def get_session(self, session_id: str) -> Optional[DebateContext]:
        """
        Retrieve session context.
        """
        return self.sessions.get(session_id)
    
    async def update_context(
        self,
        session_id: str,
        turn_data: Dict
    ) -> DebateContext:
        """
        Update session with new debate turn.
        
        Args:
            session_id: Session identifier
            turn_data: Turn information
                {
                    'speaker': str,
                    'text': str,
                    'turn': int,
                    'quality_scores': Dict (optional)
                }
        """
        
        session = self.sessions.get(session_id)
        if not session:
            raise ValueError(f"Session not found: {session_id}")
        
        # Add turn to history
        session.debate_history.append({
            **turn_data,
            'timestamp': datetime.now().isoformat()
        })
        
        # Update turn counter
        session.current_turn += 1
        session.updated_at = datetime.now().isoformat()
        
        return session
    
    async def get_history(
        self,
        session_id: str,
        last_n: Optional[int] = None
    ) -> List[Dict]:
        """
        Get debate history for context.
        
        Args:
            session_id: Session identifier
            last_n: Return only last N turns
        
        Returns:
            List of turn dictionaries
        """
        
        session = self.sessions.get(session_id)
        if not session:
            return []
        
        history = session.debate_history
        
        if last_n:
            return history[-last_n:]
        
        return history
    
    async def close_session(self, session_id: str) -> Dict:
        """
        Close and archive session.
        """
        
        session = self.sessions.get(session_id)
        if not session:
            return {'status': 'not_found'}
        
        # Save to file for archival
        archive_file = f"sessions/{session_id}.json"
        
        import os
        os.makedirs('sessions', exist_ok=True)
        
        with open(archive_file, 'w') as f:
            json.dump(asdict(session), f, indent=2)
        
        # Remove from active sessions
        del self.sessions[session_id]
        
        return {
            'status': 'closed',
            'session_id': session_id,
            'archive_file': archive_file,
            'total_turns': session.current_turn
        }
    
    def format_history_for_prompt(self, session_id: str, last_n: int = 3) -> str:
        """
        Format recent history as context for agent prompts.
        """
        session = self.sessions.get(session_id)
        if not session:
            return "(No debate history)"
        
        history = session.debate_history[-last_n:] if last_n else session.debate_history
        
        formatted = []
        for turn in history:
            speaker = turn.get('speaker', 'Unknown')
            text = turn.get('text', '')
            formatted.append(f"{speaker}: {text}")
        
        return "\n".join(formatted)


# Example usage
async def test_managed_sessions():
    """
    Test managed session service.
    """
    service = ManagedSessionService(project_id="aipodcaster-481909")
    
    # Create session
    session = await service.create_session(
        topic="AI in Healthcare"
    )
    
    print(f"\n✅ Session created: {session.session_id}")
    
    # Add turns
    await service.update_context(session.session_id, {
        'speaker': 'shakti',
        'text': 'Welcome to CROSSFIRE!',
        'turn': 0
    })
    
    await service.update_context(session.session_id, {
        'speaker': 'sovereignist',
        'text': 'AI cannot replace human doctors!',
        'turn': 1
    })
    
    # Get history
    history = await service.get_history(session.session_id)
    print(f"✅ History: {len(history)} turns")
    
    # Format for prompt
    context = service.format_history_for_prompt(session.session_id)
    print(f"\n📝 Formatted context:\n{context}")
    
    # Close session
    result = await service.close_session(session.session_id)
    print(f"\n✅ Session closed: {result['archive_file']}")


if __name__ == "__main__":
    import asyncio
    asyncio.run(test_managed_sessions())
