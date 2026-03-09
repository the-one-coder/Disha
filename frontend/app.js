// Constants
const API_BASE_URL = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1' 
    ? 'http://localhost:8000' 
    : ''; // Adjust for prod
const WS_BASE_URL = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1' 
    ? 'ws://localhost:8000' 
    : ''; // Adjust for prod

// DOM Elements
const messagesWrapper = document.getElementById('messages-wrapper');
const chatMessages = document.getElementById('chat-messages');
const chatForm = document.getElementById('chat-form');
const messageInput = document.getElementById('message-input');
const sendButton = document.getElementById('send-button');
const typingIndicator = document.getElementById('typing-indicator');
const historyLoader = document.getElementById('history-loader');
const sessionDisplay = document.getElementById('session-display');

// App State
let sessionId = localStorage.getItem('disha_session_id');
if (!sessionId) {
    // Generate simple UUID-like string for session
    sessionId = 'sess_' + Math.random().toString(36).substring(2, 15);
    localStorage.setItem('disha_session_id', sessionId);
}
sessionDisplay.textContent = sessionId.substring(0, 8) + '...';

let websocket = null;
let oldestMessageCursor = null; // ISO8601 timestamp
let isFetchingHistory = false;
let hasMoreHistory = true;

// Initialize app
function init() {
    setupWebSocket();
    fetchChatHistory();
    setupScrollListener();
    
    // Setup form submit
    chatForm.addEventListener('submit', (e) => {
        e.preventDefault();
        sendMessage();
    });
}

// -----------------------------------
// HTML Rendering
// -----------------------------------
function formatTime(isoString) {
    const date = new Date(isoString);
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
}

function parseMarkdown(text) {
    // Use marked library loaded in HTML
    if (typeof marked !== 'undefined') {
        return marked.parse(text);
    }
    return text.replace(/\n/g, '<br>');
}

function createMessageElement(msg) {
    const row = document.createElement('div');
    row.className = `message-row ${msg.role === 'user' ? 'user-row' : 'ai-row'}`;
    row.dataset.id = msg.id;
    
    const timeStr = msg.created_at ? formatTime(msg.created_at) : formatTime(new Date().toISOString());
    const contentHtml = parseMarkdown(msg.content);
    
    row.innerHTML = `
        <div class="bubble ${msg.role === 'user' ? 'user-bubble' : 'ai-bubble'}">
            <div class="bubble-content">${contentHtml}</div>
            <div class="bubble-meta">
                <span class="msg-time">${timeStr}</span>
            </div>
        </div>
    `;
    
    // Fix anchor links opening in same tab if any
    const links = row.querySelectorAll('a');
    links.forEach(a => a.target = '_blank');
    
    return row;
}

// -----------------------------------
// WebSocket Connection
// -----------------------------------
function setupWebSocket() {
    websocket = new WebSocket(`${WS_BASE_URL}/ws/chat/${sessionId}`);
    
    websocket.onopen = () => {
        console.log("WebSocket connected.");
        sendButton.disabled = false;
    };
    
    websocket.onmessage = (event) => {
        const data = JSON.parse(event.data);
        
        if (data.type === 'typing') {
            typingIndicator.style.display = data.status === 'active' ? 'flex' : 'none';
            if (data.status === 'active') {
                scrollToBottom();
            }
        } else if (data.type === 'message') {
            // New message from AI
            appendMessage(data);
            typingIndicator.style.display = 'none';
        } else if (data.type === 'error') {
            console.error("Server Error:", data.message);
            alert("Error: " + data.message);
        }
    };
    
    websocket.onclose = () => {
        console.log("WebSocket disconnected. Attempting to reconnect...");
        sendButton.disabled = true;
        setTimeout(setupWebSocket, 3000); // Auto-reconnect
    };
}

function sendMessage() {
    const content = messageInput.value.trim();
    if (!content || !websocket || websocket.readyState !== WebSocket.OPEN) return;
    
    // Optimistically render the user message
    const tempUserMsg = {
        id: 'temp-' + Date.now(),
        role: 'user',
        content: content,
        created_at: new Date().toISOString()
    };
    appendMessage(tempUserMsg);
    
    // Send over WS
    websocket.send(JSON.stringify({ content }));
    
    // Clear input
    messageInput.value = '';
}

// -----------------------------------
// Chat History (Pagination)
// -----------------------------------
async function fetchChatHistory() {
    if (isFetchingHistory || !hasMoreHistory) return;
    
    isFetchingHistory = true;
    if (oldestMessageCursor) {
        historyLoader.style.display = 'block';
    }
    
    try {
        const url = new URL(`${API_BASE_URL}/api/chat/history`);
        url.searchParams.append('session_id', sessionId);
        url.searchParams.append('limit', 20); // Fetch chunk
        
        if (oldestMessageCursor) {
            url.searchParams.append('cursor', oldestMessageCursor);
        }
        
        const response = await fetch(url);
        if (!response.ok) throw new Error('Failed to load history');
        
        const data = await response.json();
        const messages = data.messages;
        
        if (messages.length === 0) {
            hasMoreHistory = false;
            if (!oldestMessageCursor) {
                // If this is the absolute first load and it's empty, we might want to show a welcome message visually
                // (Though LangGraph onboarding agent might handle this)
            }
        } else {
            // The cursor for the NEXT page is the created_at of the oldest message in this chunk
            // The API returns chronologically (oldest element is index 0)
            oldestMessageCursor = messages[0].created_at;
            
            // Prepend elements
            const oldScrollHeight = chatMessages.scrollHeight;
            
            messages.reverse().forEach(msg => {
                const el = createMessageElement(msg);
                messagesWrapper.insertBefore(el, messagesWrapper.firstChild);
            });
            
            // If it was the first load, scroll to bottom.
            // If it was a pagination load, maintain scroll position relative to the messages that were just inserted.
            if (oldScrollHeight <= chatMessages.clientHeight) {
                scrollToBottom();
            } else {
                chatMessages.scrollTop = chatMessages.scrollHeight - oldScrollHeight;
            }
        }
    } catch(err) {
        console.error("Error fetching history:", err);
    } finally {
        isFetchingHistory = false;
        historyLoader.style.display = 'none';
    }
}

function appendMessage(msg) {
    const el = createMessageElement(msg);
    messagesWrapper.appendChild(el);
    scrollToBottom();
}

function scrollToBottom() {
    // Small delay to allow DOM to recalculate heights (especially with marked.js parsing)
    setTimeout(() => {
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }, 50);
}

function setupScrollListener() {
    chatMessages.addEventListener('scroll', () => {
        // If scrolled to top (or within 50px of top)
        if (chatMessages.scrollTop <= 50) {
            fetchChatHistory();
        }
    });
}

// Start
init();
