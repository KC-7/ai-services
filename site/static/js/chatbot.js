// Open the chatbot modal 
function openChatbot() {
    document.getElementById("chatbot-modal").style.display = "block";
}

// Close the chatbot modal
function closeChatbot() {
    document.getElementById("chatbot-modal").style.display = "none";
}

// Escape HTML to prevent XSS
function escapeHTML(str) {
    var div = document.createElement('div');
    div.appendChild(document.createTextNode(str));
    return div.innerHTML;
}

// Send message to chatbot
function sendMessage(event) {
    if (event.key === "Enter") {
        const input = document.getElementById("chatbot-input");
        const message = input.value.trim();
        if (message) {
            addMessageToChat("You", message);
            input.value = ""; // Clear the input field
            // Send message to the backend
            fetch('/chatbot', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ message: message }),
            })
                .then(response => {
                    if (!response.ok) {
                        throw new Error('Network response was not ok');
                    }
                    return response.json();
                })
                .then(data => {
                    addMessageToChat("AI Assistant", data.response);
                })
                .catch(error => {
                    console.error('There was a problem with the fetch operation:', error);
                    addMessageToChat("AI Assistant", "Sorry, I'm having trouble responding right now.");
                });
        }
    }
}

// Add message to the chat
function addMessageToChat(sender, message) {
    const chat = document.getElementById("chatbot-messages");
    const newMessage = document.createElement("div");
    newMessage.classList.add("chatbot-message");
    newMessage.innerHTML = `<strong>${escapeHTML(sender)}:</strong> ${escapeHTML(message)}`;
    chat.appendChild(newMessage);
    chat.scrollTop = chat.scrollHeight; // Scroll to the bottom
}
