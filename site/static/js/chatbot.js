// Open the chatbot modal
function openChatbot() {
    document.getElementById("chatbot-modal").style.display = "block";
}

// Close the chatbot modal
function closeChatbot() {
    document.getElementById("chatbot-modal").style.display = "none";
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
                .then(response => response.json())
                .then(data => {
                    addMessageToChat("AI Assistant", data.response);
                });
        }
    }
}

// Add message to the chat
function addMessageToChat(sender, message) {
    const chat = document.getElementById("chatbot-messages");
    const newMessage = document.createElement("div");
    newMessage.classList.add("chatbot-message");
    newMessage.innerHTML = `<strong>${sender}:</strong> ${message}`;
    chat.appendChild(newMessage);
    chat.scrollTop = chat.scrollHeight; // Scroll to the bottom
}