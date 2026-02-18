import { createDocumentPopup, createConversationPopup } from './popups.js';

const chatSection = document.querySelector('.section#chat');
const conversationSection = document.querySelector('.section#conversations');
const documentSection = document.querySelector('.section#documents');
const chatHeader = chatSection.querySelector('ul.header');
const chatConv = chatSection.querySelector('.conv');

let openedTab = {}




// ---------------- Render content-list


async function renderConversations() {
    // Request python for a content-list of conversations
    const response = await fetch('ajax/render_conversations');
    const html = await response.text();

    // Render conversations
    conversationSection.innerHTML = html;

    // Bind clicks
    const elements = conversationSection.querySelectorAll('ul.elements > li');
    elements.forEach(conversation => {
        conversation.addEventListener('click', () => {
            openConversation(conversation.dataset.id);
        });
    })

    // Bind create button
    const createButton = conversationSection.querySelector('button');
    createButton.addEventListener('click', () => {
        createConversationPopup().then(popup => {
            popup.addEventListener('conversationCreated', (event) => {
                renderConversations();
                openConversation(event.detail.sessionId);
            })
        });
    })
}

async function renderDocuments() {
    // Request python for a content-list of documents
    const response = await fetch('ajax/render_documents');
    const html = await response.text();

    // Render conversations
    documentSection.innerHTML = html;

    // Bind clicks
    const elements = documentSection.querySelectorAll('ul.elements > li');
    elements.forEach(doc => {
        doc.addEventListener('click', () => {
            openDocument(doc.dataset.id);
        });
    })

    // Bind create button
    const createButton = documentSection.querySelector('button');
    createButton.addEventListener('click', () => {
        createDocumentPopup().then(popup => {
            popup.addEventListener('documentImported', () => {
                renderDocuments();
            })
        });
    })
}


// ---------------- Manage conversations


async function openDocument(documentId) {
    // Request python for a specific conversation
    const response = await fetch(`ajax/serve_document/${documentId}`);
    const blob = await response.blob();
    const pdfUrl = URL.createObjectURL(blob);
    const newTab = window.open(pdfUrl, '_blank');

    // Release the object URL once the new tab has loaded
    newTab.onload = () => URL.revokeObjectURL(pdfUrl);
}

// ---------------- Manage conversations


async function openConversation(sessionId) {
    // Request python for a specific conversation
    const response = await fetch(`ajax/render_session/${sessionId}`);
    const content = await response.json();

    // Render tab HTML if not there yet
    let li = openedTab[sessionId];
    if (li == undefined) {
        li = document.createElement('li');
        li.innerHTML = content.tab;
        chatHeader.appendChild(li);

        li.addEventListener('click', (event) => {
            if (event.target.closest('button.close')) {
                closeConversation(sessionId);
            } else {
                openConversation(sessionId);
            }
        })

        // Save li element as opened tab
        openedTab[sessionId] = li;
    }

    // Unactive previous and active current
    chatHeader.querySelector('li.active')?.classList.remove('active');
    li.classList.add('active');

    // Render conversation HTML
    chatConv.innerHTML = content.conversation;
    const input = chatConv.querySelector('input[name="query"]');
    input.focus();

    // Bind message sent
    const chatForm = chatConv.querySelector('form.entry');
    chatForm.addEventListener('submit', (event) => {
        event.preventDefault();
        sendMessage(chatForm);
    })
}

function closeConversation(sessionId) {
    // Retrieve the tab and remove it from DOM
    const li = openedTab[sessionId];
    delete openedTab[sessionId];
    li.remove();
    
    // Open first element from opened tab if any
    const firstTabID = Object.keys(openedTab)[0];
    if (firstTabID != undefined) {
        openConversation(firstTabID);
    } else {
        chatConv.innerHTML = '';
    }
}


// ---------------- Manage messages


function displayMessage(message, role) {
    // Remove 'empty' class if present
    const currentConv = chatConv.querySelector('.chat-conversation');
    currentConv.classList.remove('empty');

    // Create message element
    const li = document.createElement('li');
    li.innerHTML = message;
    li.classList.add(role);

    // Render it
    const messageList = chatConv.querySelector('ul.messages');
    messageList.appendChild(li);
}

async function sendMessage(chatForm) {
    // Display message
    const formData = new FormData(chatForm);
    displayMessage(formData.get('query'), 'user');

    // Clear and disable user input
    chatForm.elements.query.value = '';
    chatForm.elements.query.disabled = true;

    // Send request to python
    const response = await fetch('ajax/send_message', {
        method: 'POST',
        body: formData
    });
    const content = await response.json();

    // Display response and enable user input
    displayMessage(content.response, 'assistant');

    // Enable user input
    chatForm.elements.query.disabled = false;
}





document.addEventListener('DOMContentLoaded', () => {
    // Triggered when page loaded
    renderConversations();
    renderDocuments();
})