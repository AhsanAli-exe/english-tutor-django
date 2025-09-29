from django.db import models
from django.utils import timezone

# Create your models here.

class ChatMessage(models.Model):
    # User input
    user_message = models.TextField(help_text="Original user input")
    input_method = models.CharField(max_length=10, choices=[
        ('text', 'Text'),
        ('voice', 'Voice')
    ], default='text')
    
    # AI response data
    corrected_sentence = models.TextField(help_text="Grammar-corrected version")
    has_errors = models.BooleanField(default=False, help_text="Whether grammar errors were found")
    explanation = models.TextField(blank=True, help_text="Grammar correction explanation")
    ai_response = models.TextField(help_text="AI's conversational response")
    
    # Metadata
    session_id = models.CharField(max_length=100, help_text="Session identifier")
    timestamp = models.DateTimeField(default=timezone.now)
    
    class Meta:
        ordering = ['timestamp']  # Order messages by time
        verbose_name = "Chat Message"
        verbose_name_plural = "Chat Messages"
    
    def __str__(self):
        return f"Message at {self.timestamp.strftime('%H:%M:%S')}: {self.user_message[:50]}..."
