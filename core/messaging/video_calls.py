"""
Dokets VouchAI - Video Call Integration
Supports Zoom, Google Meet, Jitsi Meet
"""

import logging
import uuid
from datetime import datetime

logger = logging.getLogger("dokets.video")

class VideoCallEngine:
    def __init__(self):
        self.meetings = []
        logger.info("Video call engine ready")
    
    def create_meeting(self, contract_id, host_id, guest_id, topic="Dispute Resolution", platform="jitsi"):
        meeting_id = f"VC-{uuid.uuid4().hex[:8].upper()}"
        room_name = f"dokets-{contract_id}-{uuid.uuid4().hex[:4]}"
        
        meeting = {
            "id": meeting_id,
            "contract_id": contract_id,
            "host_id": host_id,
            "guest_id": guest_id,
            "topic": topic,
            "platform": platform,
            "room_name": room_name,
            "jitsi_url": f"https://meet.jit.si/{room_name}",
            "zoom_url": None,
            "meet_url": f"https://meet.google.com/new?authuser=0",
            "status": "scheduled",
            "created_at": str(datetime.utcnow()),
            "started_at": None,
            "ended_at": None,
            "recording_url": None
        }
        
        self.meetings.append(meeting)
        logger.info(f"Video meeting created: {meeting_id} - {meeting['jitsi_url']}")
        return meeting
    
    def get_meeting(self, meeting_id):
        for m in self.meetings:
            if m["id"] == meeting_id:
                return m
        return None
    
    def get_contract_meetings(self, contract_id):
        return [m for m in self.meetings if m["contract_id"] == contract_id]
    
    def join_meeting(self, meeting_id):
        meeting = self.get_meeting(meeting_id)
        if meeting:
            meeting["status"] = "active"
            meeting["started_at"] = str(datetime.utcnow())
            return {
                "meeting": meeting,
                "join_url": meeting["jitsi_url"],
                "instructions": "Open the link in your browser. Enable camera and microphone when prompted."
            }
        return None

video_engine = VideoCallEngine()