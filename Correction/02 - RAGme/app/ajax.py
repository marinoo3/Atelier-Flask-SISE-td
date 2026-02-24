"""
AJAX Blueprint

Internal app API
Each route is a endpoint accessible by JS at 'ajax/[endpoint]'
"""

from typing import cast
from flask import Blueprint, render_template, url_for, send_file, jsonify, request, current_app

from app import AppContext


# Cast app_context typing
app = cast(AppContext, current_app)
# Create blueprint
ajax = Blueprint('ajax', __name__)




# ---------------
# RENDER TEMPLATES

@ajax.route('render_conversations', methods=['GET'])
def render_conversations():
    """
    Retrieve the list of all conversations (LLMSession) and render a content-list section

    Returns:
        html: content-list section html
    """
    sessions = app.rag_service.llm_handler.get_all_sessions()
    session_content = [{
        "name": sess.name,
        "id": sess.id
    } for sess in sessions]

    return render_template(
        "elements/content-list.html",
        title = "Conversations",
        element_icon = url_for('static', filename='images/conversation.svg'),
        button_icon = url_for('static', filename='images/add-conversation.svg'),
        button_text = "Nouveau chat",
        content = session_content
    )

@ajax.route('render_documents', methods=['GET'])
def render_documents():
    """
    Retrieve the list of all documents in DB and render a content-list section

    Returns:
        html: content-list section html
    """
    documents = app.document_service.get_all()
    content_documents = [{
        "name": doc.title,
        "id": doc.id
    } for doc in documents]

    return render_template(
        "elements/content-list.html",
        title = "Documents",
        element_icon = url_for('static', filename='images/document.svg'),
        button_icon = url_for('static', filename='images/add-document.svg'),
        button_text = "Ajouter",
        content = content_documents
    )

@ajax.route('render_session/<session_id>', methods=['GET'])
def render_session(session_id: str):
    """
    Retrieve a LLMSession by ID and render a chat-tab and 
    chat-conversation HTML

    Args:
        session_id (str): The ID of the session to retrieve

    Returns:
        json: {
            'tab': Tab HTML,
            'conversation': Conversation HTML
        }
    """
    session = app.rag_service.llm_handler.get_session(session_id)
    return jsonify({
        'tab': render_template(
            'elements/chat-tab.html',
            id = session.id, 
            name = session.name
        ),
        'conversation': render_template(
            'elements/chat-conversation.html',
            id = session_id,
            messages = session.get_messages()
        )
    })

@ajax.route('create_session_popup', methods=['GET'])
def create_session_popup():
    """
    Create a popup to create a new LLMSession

    Returns:
        html: Popup HTML
    """
    return render_template('elements/create-session-popup.html')

@ajax.route('create_document_popup', methods=['GET'])
def create_document_popup():
    """
    Create a popup to create a document

    Returns:
        html: Popup HTML
    """
    return render_template('elements/create-doc-popup.html')



# ---------------
# DATABASE

@ajax.route('create_document', methods=['POST'])
def create_document():
    """
    Run vectorizing pipeline and store a document in database

    Returns:
        json: Success boolean
    """
    file = request.files['file']
    app.document_service.create(
        title=file.filename or "Unknow", 
        binary=file.read(),
        category='custom'
    )

    return jsonify(success=True)

@ajax.route('serve_document/<int:document_id>', methods=['GET'])
def serve_document(document_id: int):
    """
    Search a document by ID in BDD and serve its blob on 
    a URL

    Args:
        document_id (int): ID of the document to serve

    Returns:
        json: {
            'url': served PDF URL
        }
    """
    document = app.document_service.get_by_id(document_id)
    return send_file(
        document.convert_blob(),
        mimetype='application/pdf',
        download_name=f'{document.title}.pdf'
    )




# ---------------
# RAG

@ajax.route('create_session', methods=['POST'])
def create_session():
    """
    Create a LLMSession with a specific name

    Returns:
        json: {
            'session_id': ID of the created session
        }
    """
    name = request.form.get('name', 'New chat')
    session = app.rag_service.llm_handler.create_session(name)
    return jsonify({
        'session_id': session.id
    })

@ajax.route('send_message', methods=['POST'])
def send_message():
    """
    Send a message to LLM on a specific LLMSession
    and return its response

    Returns
        json: {
            'response': LLM text response
            'context': List of chunk ID used as RAG context
        }
    """
    session_id = request.form.get('session_id')
    query = request.form.get('query')
    if session_id is None or query is None:
        return jsonify({
            'error': "Missing 'session_id' and/or 'query' argument"
        }), 400
    
    response, context = app.rag_service.make_query(query, session_id)

    return jsonify({
        'response': response,
        'context': context.model_dump() if context else None
    })