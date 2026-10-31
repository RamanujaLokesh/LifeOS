const API_URL = import.meta.env.VITE_API_URL;

async function request(path, options) {
  const res = await fetch(`${API_URL}${path}`, options);
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || `Request failed (${res.status})`);
  }
  if(res.status===204) return null;
  return res.json();
}

export function sendChat(conversationId, message) {
  return request("/api/chat", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ conversation_id: conversationId, message }),
  });
}

export function listConversations() {
  return request("/api/conversations");
}

export function getMessages(conversationId) {
  return request(`/api/conversations/${conversationId}/messages`);
}

export function deleteConversation(conversationId){
  return request(`/api/conversations/${conversationId}`,{method:"DELETE"});
}