import { request } from "./client";

export const sendChat = (conversationId, message) =>
  request("/api/chat", {
    method: "POST",
    body: JSON.stringify({ conversation_id: conversationId, message }),
  });

export const listConversations = () => request("/api/conversations");

export const getMessages = (conversationId) =>
  request(`/api/conversations/${conversationId}/messages`);

export const deleteConversation = (conversationId) =>
  request(`/api/conversations/${conversationId}`, { method: "DELETE" });