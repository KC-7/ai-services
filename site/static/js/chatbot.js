// Open the chatbot modal 
function openChatbot() {
    const chatbotModal = document.getElementById("chatbot-modal");
    const openBtn = document.getElementById("chatbot-open-btn");
    const minimizedBtn = document.getElementById("chatbot-minimized-btn");

    chatbotModal.style.display = "block";
    openBtn.style.display = "none"; // Hide the teal "new chat" button
    minimizedBtn.style.display = "none"; // Hide the minimized button
    chatbotModal.classList.remove('maximized');
}

// Close the chatbot modal and reset the conversation
function closeChatbot() {
    const openBtn = document.getElementById("chatbot-open-btn");
    const minimizedBtn = document.getElementById("chatbot-minimized-btn");

    document.getElementById("chatbot-modal").style.display = "none";
    document.getElementById("chatbot-messages").innerHTML = ""; // Reset the conversation
    openBtn.style.display = "block"; // Show the teal "new chat" button
    minimizedBtn.style.display = "none"; // Hide the minimized button
}

// Minimize the chatbot modal without clearing chat
function minimizeChatbot() {
    const chatbotModal = document.getElementById("chatbot-modal");
    const openBtn = document.getElementById("chatbot-open-btn");
    const minimizedBtn = document.getElementById("chatbot-minimized-btn");

    chatbotModal.style.display = "none"; // Hide the modal
    openBtn.style.display = "none"; // Hide the teal "new chat" button
    minimizedBtn.style.display = "block"; // Show the purple minimized button

    // Explicitly change button background to purple when minimized
    minimizedBtn.classList.add('purple-btn'); // Add the purple class
}

// Toggle size for chatbot modal
function toggleMaximizeChatbot() {
    const chatbotModal = document.getElementById("chatbot-modal");
    const toggleButton = document.getElementById("toggle-maximize");

    if (chatbotModal.classList.contains('maximized')) {
        chatbotModal.classList.remove('maximized');
        toggleButton.innerHTML = "<i class='fas fa-expand'></i>"; // Maximize icon
    } else {
        chatbotModal.classList.add('maximized');
        toggleButton.innerHTML = "<i class='fas fa-compress'></i>"; // Minimize icon
    }
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
            .then(response => response.json())
            .then(data => {
                if (data && data.response) {
                    addMessageToChat("AI", data.response);
                }
            });
        }
    }
}

// Add message to the chat window
function addMessageToChat(sender, message, isAI = false) {
    const messagesContainer = document.getElementById("chatbot-messages");
    const newMessage = document.createElement("div");
    newMessage.classList.add("message");

    if (isAI) {
        // Convert AI response from Markdown to HTML using Marked.js
        const formattedMessage = marked(message); // Converts Markdown into HTML
        newMessage.innerHTML = `<strong>${sender}:</strong> ${formattedMessage}`;
    } else {
        // Escape user input to prevent XSS
        newMessage.innerHTML = `<strong>${sender}:</strong> ${escapeHTML(message)}`;
    }

    messagesContainer.appendChild(newMessage);
    messagesContainer.scrollTop = messagesContainer.scrollHeight; // Auto-scroll to the bottom
}
