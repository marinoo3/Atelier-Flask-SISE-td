function renderPopup(html) {
    // Render popup
    const popup = document.createElement('div');
    popup.insertAdjacentHTML('beforeend', html);
    popup.classList.add('popup-wrapper');
    document.body.appendChild(popup);
    // Remove popup if click outside
    document.addEventListener('click', (e) => {
        if (!e.target.closest('.popup')) {
            popup.remove();
        }
    })
    // Return popup element
    return popup
}

async function createConversationPopup() {
    // Request popup HTML to Python
    const response = await fetch('ajax/create_session_popup');
    const html = await response.text();

    // Render popup
    const popup = renderPopup(html);
    const formElement = popup.querySelector('form');

     // On cancled clicked
    formElement.addEventListener('reset', () => {
        popup.remove();
    })

    // On add clicked
    formElement.addEventListener('submit', async (event) => {
        event.preventDefault();

        // Create new LLM conversation in Python
        const formData = new FormData(formElement);
        const response = await fetch('ajax/create_session', {
            method: 'POST',
            body: formData
        })
        const content = await response.json();

        // TODO: create custom event `conversationCreated`
        // with sessionId as detail and bubbles

        popup.remove();
    })

    return popup
}

async function createDocumentPopup() {
    // Request popup HTML to Python
    const response = await fetch('ajax/create_document_popup');
    const html = await response.text();

    // Render popup
    const popup = renderPopup(html);
    const formElement = popup.querySelector('form');

    // On cancled clicked
    formElement.addEventListener('reset', () => {
        popup.remove();
    })

    // On add clicked
    formElement.addEventListener('submit', async (event) => {
        event.preventDefault();

        // Save document in BDD
        const formData = new FormData(formElement);
        await fetch('ajax/create_document', {
            method: 'POST',
            body: formData
        })

        // TODO: create custom event `documentImported`
        // with file (formElement.elements.file.value) as detail and bubbles

        popup.remove();
    })
    // Return popup
    return popup
}