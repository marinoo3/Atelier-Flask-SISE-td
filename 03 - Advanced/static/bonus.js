// ============================================================================
// Flask Bonus - JavaScript Interactions
// ============================================================================

// Global variables
let availableRoutes = {};
let currentRoute = null;

// ============================================================================
// DOM Elements
// ============================================================================

const methodSelect = document.getElementById('methodSelect');
const urlInput = document.getElementById('urlInput');
const paramsInput = document.getElementById('paramsInput');
const bodyInput = document.getElementById('bodyInput');
const sendBtn = document.getElementById('sendBtn');
const sendBtnText = document.getElementById('sendBtnText');
const sendBtnLoader = document.getElementById('sendBtnLoader');
const clearBtn = document.getElementById('clearBtn');
const responseContainer = document.getElementById('responseContainer');
const routesListContainer = document.getElementById('routesListContainer');
const paramsListContainer = document.getElementById('paramsListContainer');
const paramsList = document.getElementById('paramsList');

// ============================================================================
// Initialization
// ============================================================================

// Load routes on startup
document.addEventListener('DOMContentLoaded', async () => {
    await loadRoutes();
});

// ============================================================================
// Event Listeners
// ============================================================================

// Send button
sendBtn.addEventListener('click', sendRequest);

// Clear button
clearBtn.addEventListener('click', clearForm);

// Enter to send (on inputs)
[urlInput, paramsInput, bodyInput].forEach(input => {
    input.addEventListener('keydown', function(e) {
        if (e.ctrlKey && e.key === 'Enter') {
            sendRequest();
        }
    });
});

// ============================================================================
// Functions - Loading routes
// ============================================================================

/**
 * Load the list of routes from the API
 */
async function loadRoutes() {
    try {
        const response = await fetch('/api/routes');
        const data = await response.json();
        
        if (data.status === 'success' && data.routes) {
            availableRoutes = data.routes;
            renderRoutesList();
        } else {
            showRoutesError('Unable to load routes');
        }
    } catch (error) {
        showRoutesError(`Error: ${error.message}`);
    }
}

/**
 * Display the list of routes in the sidebar
 */
function renderRoutesList() {
    if (Object.keys(availableRoutes).length === 0) {
        routesListContainer.innerHTML = `
            <div class="empty-state">
                <p>No routes available</p>
            </div>
        `;
        return;
    }
    
    let html = '';
    
    for (const [key, route] of Object.entries(availableRoutes)) {
        // Determine the main method
        const mainMethod = route.methods[0];
        const methodClass = `method-${mainMethod.toLowerCase()}`;
        
        html += `
            <div class="route-item" data-route-key="${key}">
                <div>
                    <span class="method ${methodClass}">${mainMethod}</span>
                    <span class="route-path">${route.path}</span>
                    ${route.description ? `<span class="route-description">${route.description}</span>` : ''}
                </div>
            </div>
        `;
    }
    
    routesListContainer.innerHTML = html;
    
    // Add event listeners
    const routeItems = routesListContainer.querySelectorAll('.route-item');
    routeItems.forEach(item => {
        item.addEventListener('click', function() {
            const routeKey = this.getAttribute('data-route-key');
            loadRoute(routeKey);
            
            // Highlight the active item
            routeItems.forEach(r => r.classList.remove('active'));
            this.classList.add('active');
        });
    });
}

/**
 * Display an error when loading routes
 */
function showRoutesError(message) {
    routesListContainer.innerHTML = `
        <div class="empty-state" style="color: var(--error);">
            <p>❌ ${message}</p>
        </div>
    `;
}

/**
 * Load a specific route
 */
function loadRoute(routeKey) {
    const route = availableRoutes[routeKey];
    if (!route) return;
    
    currentRoute = route;
    
    // Fill the fields
    methodSelect.value = route.methods[0];
    urlInput.value = route.path;
    
    // Prepare parameters
    if (route.params && route.params.length > 0) {
        displayParams(route.params);
        
        // Generate an example query string for GET parameters
        if (route.methods.includes('GET')) {
            const queryString = route.params
                .filter(p => p.default !== undefined)
                .map(p => `${p.name}=${p.default}`)
                .join('&');
            paramsInput.value = queryString;
        }
    } else {
        paramsListContainer.style.display = 'none';
        paramsInput.value = '';
    }
    
    // Prepare the body
    if (route.body_example) {
        bodyInput.value = JSON.stringify(route.body_example, null, 2);
    } else {
        bodyInput.value = '';
    }
    
    // Display a message in the response area
    responseContainer.innerHTML = `
        <div class="empty-state">
            <p>Request loaded: <strong>${route.methods[0]} ${route.path}</strong></p>
            ${route.description ? `<p class="hint">${route.description}</p>` : ''}
            <p class="hint">Click "Send Request" to execute</p>
        </div>
    `;
}

/**
 * Display the parameters list
 */
function displayParams(params) {
    if (!params || params.length === 0) {
        paramsListContainer.style.display = 'none';
        return;
    }
    
    let html = '';
    params.forEach(param => {
        html += `
            <div class="param-item">
                <div>
                    <span class="param-name">${param.name}</span>
                    <span class="param-type">${param.type}</span>
                    ${param.required ? '<span class="param-required">*required</span>' : ''}
                </div>
                ${param.description ? `<div class="param-description">${param.description}</div>` : ''}
                ${param.default !== undefined ? `<div class="param-default">Default: ${param.default}</div>` : ''}
            </div>
        `;
    });
    
    paramsList.innerHTML = html;
    paramsListContainer.style.display = 'block';
}

/**
 * Send the request
 */
async function sendRequest() {
    const method = methodSelect.value;
    let url = urlInput.value.trim();
    const params = paramsInput.value.trim();
    let body = bodyInput.value.trim();
    const apiKey = document.getElementById('apiKeyInput')?.value.trim();
    
    // Validation
    if (!url) {
        showError('Please enter a URL');
        return;
    }
    
    // Build the URL with parameters
    if (params && method === 'GET') {
        url += (url.includes('?') ? '&' : '?') + params;
    }
    
    // Prepare request options
    const options = {
        method: method,
        headers: {
            'Content-Type': 'application/json',
        }
    };
    
    // Add API key to headers if provided
    if (apiKey) {
        options.headers['X-API-Key'] = apiKey;
    }
    
    // Add the body if necessary
    if (body && (method === 'POST' || method === 'PUT')) {
        try {
            // Check if it's valid JSON
            JSON.parse(body);
            options.body = body;
        } catch (e) {
            showError('The request body is not valid JSON');
            return;
        }
    }
    
    // Show the loader
    sendBtnText.style.display = 'none';
    sendBtnLoader.style.display = 'inline';
    sendBtn.disabled = true;
    
    try {
        // Record start time
        const startTime = performance.now();
        
        // Send the request
        const response = await fetch(url, options);
        
        // Calculate response time
        const responseTime = Math.round(performance.now() - startTime);
        
        // Get the content
        const contentType = response.headers.get('content-type');
        let data;
        
        if (contentType && contentType.includes('application/json')) {
            data = await response.json();
        } else {
            data = await response.text();
        }
        
        // Display the response
        displayResponse(response, data, responseTime);
        
    } catch (error) {
        showError(`Error sending request: ${error.message}`);
    } finally {
        // Hide the loader
        sendBtnText.style.display = 'inline';
        sendBtnLoader.style.display = 'none';
        sendBtn.disabled = false;
    }
}

/**
 * Display the response
 */
function displayResponse(response, data, responseTime) {
    const statusClass = response.ok ? 'status-success' : 'status-error';
    const statusText = response.ok ? '✓ Success' : '✗ Error';
    
    // Format data for display
    let formattedData;
    if (typeof data === 'object') {
        formattedData = JSON.stringify(data, null, 2);
    } else {
        formattedData = data;
    }
    
    responseContainer.innerHTML = `
        <div class="response-header">
            <div>
                <span class="status-badge ${statusClass}">${statusText}</span>
                <span style="margin-left: 12px;">Status: ${response.status} ${response.statusText}</span>
            </div>
            <div>
                <span>⏱️ ${responseTime}ms</span>
            </div>
        </div>
        <div class="response-body">
            <pre>${escapeHtml(formattedData)}</pre>
        </div>
    `;
}

/**
 * Display an error
 */
function showError(message) {
    responseContainer.innerHTML = `
        <div class="response-header">
            <div>
                <span class="status-badge status-error">✗ Error</span>
            </div>
        </div>
        <div class="response-body">
            <pre>${escapeHtml(message)}</pre>
        </div>
    `;
}

/**
 * Clear the form
 */
function clearForm() {
    currentRoute = null;
    methodSelect.value = 'GET';
    urlInput.value = '';
    paramsInput.value = '';
    bodyInput.value = '';
    
    // Hide the parameters list
    paramsListContainer.style.display = 'none';
    
    responseContainer.innerHTML = `
        <div class="empty-state">
            <p>No request sent yet</p>
            <p class="hint">Select a request from the list or configure one manually</p>
        </div>
    `;
    
    // Remove active class from all route items
    const routeItems = routesListContainer.querySelectorAll('.route-item');
    routeItems.forEach(r => r.classList.remove('active'));
}

/**
 * Escape HTML to prevent injections
 */
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// ============================================================================
// Startup messages
// ============================================================================

console.log('🧪 Flask Bonus - Interface ready!');
console.log('💡 Tip: Use Ctrl+Enter to quickly send a request');
