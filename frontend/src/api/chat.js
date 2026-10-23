const API_URL = import.meta.env.VITE_API_URL;


export async function sendChat(messages){
    const res = await fetch(`${API_URL}/api/chat`,{
        method: 'POST',
        headers: {"content-type": "application/json"},
        body: JSON.stringify({messages})
    });
    if (!res.ok){
        const err  = await res.json().catch(()=>({}));
        throw new Error(err.detail || "Failed to send chat message");
    }
    const data = await res.json();
    return data.reply;
}