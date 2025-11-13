from sqlalchemy.orm import Session
from app.models.chat_conversation import ChatConversation
from app.models.chat_message import ChatMessage
from datetime import datetime


class ChatbotService:
    """Service for managing chatbot conversations and messages"""

    @staticmethod
    def create_conversation(db: Session, user_id: int, title: str = None) -> ChatConversation:
        """Create a new conversation"""
        conversation = ChatConversation(
            user_id=user_id,
            title=title or f"Chat {datetime.utcnow().strftime('%Y-%m-%d %H:%M')}"
        )
        db.add(conversation)
        db.commit()
        db.refresh(conversation)
        return conversation

    @staticmethod
    def get_conversation(db: Session, conversation_id: int, user_id: int) -> ChatConversation:
        """Get a conversation by ID (verify user owns it)"""
        return db.query(ChatConversation).filter(
            ChatConversation.conversation_id == conversation_id,
            ChatConversation.user_id == user_id
        ).first()

    @staticmethod
    def get_user_conversations(db: Session, user_id: int, limit: int = 10) -> list:
        """Get all conversations for a user"""
        return db.query(ChatConversation).filter(
            ChatConversation.user_id == user_id
        ).order_by(ChatConversation.updated_at.desc()).limit(limit).all()

    @staticmethod
    def add_message(db: Session, conversation_id: int, content: str) -> ChatMessage:
        """Add a message to a conversation"""
        message = ChatMessage(
            conversation_id=conversation_id,
            content=content
        )
        db.add(message)
        db.commit()
        db.refresh(message)
        return message

    @staticmethod
    def get_conversation_messages(db: Session, conversation_id: int) -> list:
        """Get all messages in a conversation"""
        return db.query(ChatMessage).filter(
            ChatMessage.conversation_id == conversation_id
        ).order_by(ChatMessage.created_at.asc()).all()

    @staticmethod
    def delete_conversation(db: Session, conversation_id: int, user_id: int) -> bool:
        """Delete a conversation (verify user owns it)"""
        conversation = db.query(ChatConversation).filter(
            ChatConversation.conversation_id == conversation_id,
            ChatConversation.user_id == user_id
        ).first()

        if conversation:
            db.delete(conversation)
            db.commit()
            return True
        return False

    @staticmethod
    def delete_conversation(db: Session, conversation_id: int, user_id: int) -> bool:
        """Delete a conversation and all its messages (verify user owns it)"""
        try:
            # Verify conversation exists and user owns it
            conversation = db.query(ChatConversation).filter(
                ChatConversation.conversation_id == conversation_id,
                ChatConversation.user_id == user_id
            ).first()

            if not conversation:
                return False

            # Step 1: Delete all messages first (to avoid foreign key constraint)
            db.query(ChatMessage).filter(
                ChatMessage.conversation_id == conversation_id
            ).delete(synchronize_session=False)
            
            # Step 2: Then delete the conversation
            db.delete(conversation)
            db.commit()
            
            return True
        except Exception as e:
            db.rollback()
            raise e