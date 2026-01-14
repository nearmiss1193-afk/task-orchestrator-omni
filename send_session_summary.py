"""
Entry point to send session summary email.
Wrapper around modules.communications.reliable_email to ensure consistent logic.
"""
from modules.communications.reliable_email import send_session_summary

if __name__ == "__main__":
    print("🚀 Initiating Session Summary Protocol...")
    send_session_summary()
