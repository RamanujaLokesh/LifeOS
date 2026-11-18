import { request } from "./client";

export const listMemories = (status) =>
  request(`/api/memories${status ? `?status=${status}` : ""}`);

export const approveMemory = (id) =>
  request(`/api/memories/${id}/approve`, { method: "POST" });

export const deleteMemory = (id) =>
  request(`/api/memories/${id}`, { method: "DELETE" });