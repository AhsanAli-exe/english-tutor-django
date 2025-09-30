from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from openai import OpenAI
import json
# Audio processing imports removed - now using browser Web Speech API
import uuid
from .models import ChatMessage
import warnings
warnings.filterwarnings("ignore", message="FP16 is not supported on CPU; using FP32 instead")

# Create your views here.
# Note: Audio transcription now handled by browser's Web Speech API

GROQ_API_KEY = "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"
GROQ_MODEL = "llama-3.3-70b-versatile"


def chat_interface(request):
    """
    Main chat interface view
    This renders the chat page where users can interact with the tutor
    """
    # Get or create a session ID for this user
    if 'session_id' not in request.session:
        request.session['session_id'] = str(uuid.uuid4())
    
    # Get recent chat history for this session
    session_id = request.session['session_id']
    recent_messages = ChatMessage.objects.filter(session_id=session_id).order_by('timestamp')[:50]
    
    context = {
        'session_id': session_id,
        'recent_messages': recent_messages,
    }
    
    return render(request, 'tutor_chat/chat_interface.html', context)


def call_groq(user_text, session_id):
    client = OpenAI(
        api_key=GROQ_API_KEY,
        base_url="https://api.groq.com/openai/v1",
    )
    system_message = """You are Alex, a friendly English conversation partner. You help with REAL grammar mistakes while having natural conversations.

FOCUS: Only fix grammar errors that actually sound wrong when spoken.

CORRECT these errors:
- "I are happy" → "I am happy" (wrong verb)
- "He don't know" → "He doesn't know" (wrong verb form)
- "I have 25 years old" → "I am 25 years old" (wrong verb)

DO NOT correct these (they're natural speech):
- Missing punctuation or capitalization
- Natural conversation flow
- Casual phrasing
- Incomplete sentences that make sense in context

Be conversational and engaging. Only mark has_errors=true for real grammar mistakes.

Return JSON:
{
    "corrected_sentence": "corrected version if needed",
    "has_errors": true_or_false,
    "explanation": "brief friendly explanation if error exists",
    "conversational_response": "engaging response to continue conversation"
}"""
    user_message = f"""USER'S MESSAGE: "{user_text}"

EXAMPLES:
User: "I are very sad"
Output: {{"corrected_sentence": "I am very sad", "has_errors": true, "explanation": "We say 'I am' not 'I are'", "conversational_response": "I'm sorry to hear you're feeling sad. What's bothering you?"}}

User: "the movie was amazing and i loved it"
Output: {{"corrected_sentence": "the movie was amazing and i loved it", "has_errors": false, "explanation": "", "conversational_response": "That's wonderful! What movie was it? I'd love to hear what you enjoyed about it."}}

User: "favourite scene is when batman fights joker"  
Output: {{"corrected_sentence": "favourite scene is when batman fights joker", "has_errors": false, "explanation": "", "conversational_response": "Great choice! That's such an intense scene. The chemistry between those characters is incredible."}}

Now analyze and return JSON."""

    # Get conversation history from database for context (like Final_Version.py)
    recent_messages = ChatMessage.objects.filter(session_id=session_id).order_by('timestamp')[-5:]  # Last 5 messages for context

    # Build conversation history for AI
    conversation_messages = [{"role": "system", "content": system_message}]

    # Add recent conversation history
    for msg in recent_messages:
        conversation_messages.append({"role": "user", "content": msg.user_message})
        conversation_messages.append({"role": "assistant", "content": msg.ai_response})

    # Add current message
    conversation_messages.append({"role": "user", "content": user_message})

    try:
        response = client.chat.completions.create(
                model = GROQ_MODEL,
                messages = conversation_messages,  # Now includes conversation history!
                temperature = 0.3,
                max_tokens = 500
            )
        content = response.choices[0].message.content.strip()
        
        if content.startswith("```json"):
            content = content[7:-3].strip()
        elif content.startswith("```"):
            content = content[3:-3].strip()
        
        ai_result = json.loads(content)
        return ai_result
    except Exception as e:
        print(f"Groq API error: {e}")
        return {
            "corrected_sentence": user_text, "has_errors": False, "explanation": "",
            "conversational_response": "I'm having a little trouble connecting right now. Let's talk about something else."
        }


@csrf_exempt
def clear_history(request):
    if request.method == 'POST':
        try:
            session_id = request.session.get('session_id')
            if session_id:
                ChatMessage.objects.filter(session_id=session_id).delete()
                print(f"Cleared chat history for session {session_id}")
            return JsonResponse({'success': True,'message': 'Chat history cleared'})
        except Exception as e:
            print(f"Error clearing chat history: {e}")
            return JsonResponse({'success': False,'message': 'Failed to clear chat history'}, status=500)
    return JsonResponse({'error': 'Only POST method allowed'}, status=405)


@csrf_exempt
def process_message(request):
    """
    Process user message and return AI response
    This will integrate with your existing EnglishTutor logic
    """
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            input_method = data.get('input_method','text')
            session_id = request.session.get('session_id')
            # Both voice and text now use the same message field (browser handles voice transcription)
            user_message = data.get('message', '').strip()
            if not user_message:
                return JsonResponse({'error': 'Message cannot be empty'}, status=400)
            
            transcription = user_message  # For voice, this is already transcribed by browser
            
            
            ai_response = call_groq(user_message, session_id)
            
            # Save message to database
            chat_message = ChatMessage.objects.create(
                user_message=user_message,
                input_method=input_method,
                corrected_sentence=ai_response['corrected_sentence'],
                has_errors=ai_response['has_errors'],
                explanation=ai_response['explanation'],
                ai_response=ai_response['conversational_response'],
                session_id=session_id
            )
            
            return JsonResponse({
                'success': True,
                'transcription': transcription,
                'ai_response': ai_response['conversational_response'],
                'corrected_sentence': ai_response['corrected_sentence'],
                'has_errors': ai_response['has_errors'],
                'explanation': ai_response['explanation'],
                'message_id': chat_message.id
            })
            
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON data'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    return JsonResponse({'error': 'Only POST method allowed'}, status=405)
