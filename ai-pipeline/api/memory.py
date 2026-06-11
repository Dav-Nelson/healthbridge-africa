# api/memory.py

conversation_memory = {}


def get_history(session_id: str):
    return conversation_memory.get(session_id, [])


def add_message(session_id: str, role: str, content: str):
    if session_id not in conversation_memory:
        conversation_memory[session_id] = []

    conversation_memory[session_id].append({
        "role": role,
        "content": content
    })

    # keep only last 20 messages
    conversation_memory[session_id] = conversation_memory[session_id][-20:]