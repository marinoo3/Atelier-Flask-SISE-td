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
        // TODO: create popup and rerender + open session on session creation
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


// ---------------- Manage documents


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
    // TODO: request `render_session` endpoint with the `sessionId` as URL parameter
    // and read its json content

    // Render tab HTML if not there yet
    let li = openedTab[sessionId];
    if (li == undefined) {

        // TODO: create a `li` element, set its innerHTML to the `tab` value of the response content
        // and append this new li element to the `chatHeader`

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

    // TODO: set the `chatConv` innerHTML to the `conversation` key of the response content

    const input = chatConv.querySelector('input[name="query"]');
    input.focus();

    // Bind message sent
    const chatForm = chatConv.querySelector('form.entry');

    // TODO: add event listener on form submit, prevent default event and call `sendMessage` function 
}

function closeConversation(sessionId) {
    // Retrieve the tab and remove it from DOM
    const li = openedTab[sessionId];
    delete openedTab[sessionId];
    li.remove();
    
    // Render first of opened tab if any
    const firstTabID = Object.keys(openedTab)[0];
    if (firstTabID != undefined) {
        openConversation(firstTabID);
    } else {
        chatConv.innerHTML = '';
    }
}


// ---------------- Manage messages


async function sendMessage(chatForm) {
    // Display message
    const formData = new FormData(chatForm);

    // TODO: call `displayMessage` with the user query as message and "user" as role
    // TIPS: retrieve user query from `formData`

    // Clear and disable user input
    chatForm.elements.query.value = '';
    chatForm.elements.query.disabled = true;

    // TODO: request `send_message` endpoint with the `formData` as body
    // and read the response json content

    // TODO: call `displayMessage` with the response content `response` value and "assistant" as role

    // Enable user input
    chatForm.elements.query.disabled = false;
}