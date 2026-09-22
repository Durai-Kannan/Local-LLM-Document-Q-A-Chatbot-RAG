document.addEventListener('DOMContentLoaded', () => {
    // DOM Elements
    const healthDot = document.getElementById('health-status-dot');
    const healthText = document.getElementById('health-status-text');
    const healthModel = document.getElementById('health-model-name');
    
    const dropZone = document.getElementById('drop-zone');
    const fileInput = document.getElementById('file-input');
    const uploadProgress = document.getElementById('upload-progress');
    const uploadStatusText = document.getElementById('upload-status-text');
    
    const docList = document.getElementById('document-list');
    const docCount = document.getElementById('doc-count');
    const refreshDocsBtn = document.getElementById('refresh-docs-btn');
    
    const chatViewport = document.getElementById('chat-viewport');
    const chatMessages = document.getElementById('chat-messages');
    const welcomeCard = document.getElementById('welcome-card');
    const chatForm = document.getElementById('chat-form');
    const userInput = document.getElementById('user-input');
    const sendBtn = document.getElementById('send-btn');
    const clearChatBtn = document.getElementById('clear-chat-btn');
    
    const sidebar = document.getElementById('sidebar');
    const toggleSidebarBtn = document.getElementById('toggle-sidebar');
    const closeSidebarMobileBtn = document.getElementById('close-sidebar-mobile');
    const sidebarBackdrop = document.getElementById('sidebar-backdrop');
    
    const sourceModal = document.getElementById('source-modal');
    const closeModalBtn = document.getElementById('close-modal-btn');
    const modalDoneBtn = document.getElementById('modal-done-btn');
    const modalCopyBtn = document.getElementById('modal-copy-btn');
    const modalTitle = document.getElementById('modal-title');
    const modalMeta = document.getElementById('modal-meta');
    const modalContent = document.getElementById('modal-content');

    // Auto-resize textarea
    userInput.addEventListener('input', () => {
        userInput.style.height = 'auto';
        userInput.style.height = Math.min(userInput.scrollHeight, 140) + 'px';
    });

    // Enter key submits (Shift+Enter for newline)
    userInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            chatForm.dispatchEvent(new Event('submit'));
        }
    });

    // Suggestion chips handler
    document.querySelectorAll('.suggestion-chip').forEach(chip => {
        chip.addEventListener('click', () => {
            const promptText = chip.getAttribute('data-prompt');
            if (promptText) {
                userInput.value = promptText;
                userInput.focus();
                userInput.dispatchEvent(new Event('input'));
            }
        });
    });

    // Mobile / Responsive Sidebar Toggle
    function openSidebar() {
        sidebar.classList.add('open');
        sidebarBackdrop.classList.add('active');
    }

    function closeSidebar() {
        sidebar.classList.remove('open');
        sidebarBackdrop.classList.remove('active');
    }

    if (toggleSidebarBtn) toggleSidebarBtn.addEventListener('click', () => {
        if (sidebar.classList.contains('open')) {
            closeSidebar();
        } else {
            openSidebar();
        }
    });

    if (closeSidebarMobileBtn) closeSidebarMobileBtn.addEventListener('click', closeSidebar);
    if (sidebarBackdrop) sidebarBackdrop.addEventListener('click', closeSidebar);

    // Health Check Polling
    async function checkHealth() {
        try {
            const res = await fetch('/api/health');
            const data = await res.json();
            
            if (data.status === 'ok') {
                healthDot.className = 'status-indicator status-online';
                healthText.textContent = 'System Online';
            } else if (data.ollama) {
                healthDot.className = 'status-indicator status-connecting';
                healthText.textContent = `Loading model ${data.ollama_model}`;
            } else {
                healthDot.className = 'status-indicator status-offline';
                healthText.textContent = 'Ollama Offline';
            }
            healthModel.textContent = `${data.ollama_model || 'Model'} • ${data.total_chunks || 0} chunks`;
        } catch (err) {
            healthDot.className = 'status-indicator status-offline';
            healthText.textContent = 'Server Disconnected';
            healthModel.textContent = 'Check local server';
        }
    }

    checkHealth();
    setInterval(checkHealth, 15000);

    // Fetch and render document list
    async function loadDocuments() {
        try {
            const res = await fetch('/api/documents');
            const data = await res.json();
            docCount.textContent = data.total || 0;

            if (!data.documents || data.documents.length === 0) {
                docList.innerHTML = `
                    <div class="empty-docs-state">
                        <i class="fa-regular fa-folder-open"></i>
                        <p>No documents in knowledge base</p>
                    </div>`;
                return;
            }

            docList.innerHTML = data.documents.map(doc => {
                const iconClass = getFileIcon(doc.file_type);
                return `
                    <div class="doc-card" data-id="${doc.document_id}">
                        <div class="doc-card-info">
                            <i class="${iconClass} doc-card-icon"></i>
                            <div class="doc-card-text">
                                <span class="doc-card-name" title="${escapeHtml(doc.file_name)}">${escapeHtml(doc.file_name)}</span>
                                <span class="doc-card-meta">${doc.total_chunks} chunk${doc.total_chunks === 1 ? '' : 's'}</span>
                            </div>
                        </div>
                        <button class="doc-delete-btn" onclick="deleteDocument('${doc.document_id}', '${escapeHtml(doc.file_name)}')" title="Delete document">
                            <i class="fa-regular fa-trash-can"></i>
                        </button>
                    </div>`;
            }).join('');
        } catch (err) {
            console.error("Error loading documents:", err);
        }
    }

    function getFileIcon(ext) {
        switch((ext || '').toLowerCase()) {
            case '.pdf': return 'fa-regular fa-file-pdf';
            case '.docx': return 'fa-regular fa-file-word';
            case '.md': return 'fa-regular fa-file-code';
            default: return 'fa-regular fa-file-lines';
        }
    }

    refreshDocsBtn.addEventListener('click', loadDocuments);
    loadDocuments();

    // Delete Document
    window.deleteDocument = async (docId, fileName) => {
        if (!confirm(`Are you sure you want to remove '${fileName}' from ChromaDB?`)) return;

        try {
            const res = await fetch(`/api/documents/${docId}`, { method: 'DELETE' });
            if (res.ok) {
                loadDocuments();
                checkHealth();
            } else {
                alert("Failed to delete document.");
            }
        } catch (err) {
            alert("Error deleting document: " + err.message);
        }
    };

    // File Upload Handling
    dropZone.addEventListener('click', () => fileInput.click());

    dropZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        dropZone.classList.add('dragover');
    });

    dropZone.addEventListener('dragleave', () => dropZone.classList.remove('dragover'));

    dropZone.addEventListener('drop', (e) => {
        e.preventDefault();
        dropZone.classList.remove('dragover');
        if (e.dataTransfer.files.length > 0) {
            uploadFile(e.dataTransfer.files[0]);
        }
    });

    fileInput.addEventListener('change', () => {
        if (fileInput.files.length > 0) {
            uploadFile(fileInput.files[0]);
        }
    });

    async function uploadFile(file) {
        const formData = new FormData();
        formData.append('file', file);

        uploadProgress.style.display = 'flex';
        uploadStatusText.textContent = `Uploading ${file.name}...`;

        try {
            const res = await fetch('/api/documents/upload', {
                method: 'POST',
                body: formData
            });

            const data = await res.json();
            if (!res.ok) {
                throw new Error(data.detail || 'Upload failed');
            }

            uploadStatusText.textContent = `Indexed ${data.total_chunks} chunks!`;
            setTimeout(() => { uploadProgress.style.display = 'none'; }, 2000);
            
            loadDocuments();
            checkHealth();
        } catch (err) {
            alert(`Upload Error: ${err.message}`);
            uploadProgress.style.display = 'none';
        } finally {
            fileInput.value = '';
        }
    }

    // Clear Chat Session
    clearChatBtn.addEventListener('click', () => {
        chatMessages.innerHTML = '';
        welcomeCard.style.display = 'block';
    });

    // Chat Submission
    chatForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const question = userInput.value.trim();
        if (!question) return;

        // Hide welcome card on first message
        if (welcomeCard) welcomeCard.style.display = 'none';

        // Render User Message
        appendMessage('user', question);
        userInput.value = '';
        userInput.style.height = 'auto';

        // Render Assistant Loading State
        const loadingId = appendLoadingMessage();
        sendBtn.disabled = true;

        try {
            const res = await fetch('/api/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ question })
            });

            const data = await res.json();
            removeMessage(loadingId);

            if (!res.ok) {
                throw new Error(data.detail || 'Failed to get answer');
            }

            appendMessage('assistant', data.answer, data.sources);
        } catch (err) {
            removeMessage(loadingId);
            appendMessage('assistant', `⚠️ **Error**: ${err.message}`, []);
        } finally {
            sendBtn.disabled = false;
        }
    });

    function appendMessage(role, content, sources = []) {
        const msgDiv = document.createElement('div');
        msgDiv.className = `chat-bubble-row ${role}`;

        const avatar = role === 'user' 
            ? '<div class="chat-avatar"><i class="fa-regular fa-user"></i></div>' 
            : '<div class="chat-avatar"><i class="fa-solid fa-sparkles"></i></div>';

        let sourcesHtml = '';
        if (sources && sources.length > 0) {
            const badges = sources.map((src, i) => {
                const score = src.relevance_score ? `${Math.round(src.relevance_score * 100)}%` : '';
                const pageStr = src.page ? `Page ${src.page}` : 'Doc';
                const safeSnippet = escapeHtml(src.snippet || '');
                const safeDoc = escapeHtml(src.document);

                return `
                    <button class="citation-pill-btn" onclick="openSourceModal('${safeDoc}', '${pageStr}', '${src.chunk_id}', '${score}', \`${safeSnippet}\`)">
                        <i class="fa-regular fa-bookmark"></i>
                        <span>[${i+1}] ${safeDoc} (${pageStr})</span>
                        ${score ? `<span class="citation-score-badge">${score}</span>` : ''}
                    </button>`;
            }).join('');

            sourcesHtml = `
                <div class="citation-container">
                    <div class="citation-header">
                        <i class="fa-solid fa-quote-left"></i> Sources (${sources.length})
                    </div>
                    <div class="citation-list">${badges}</div>
                </div>`;
        }

        msgDiv.innerHTML = `
            ${avatar}
            <div class="chat-bubble-content">
                <div>${formatMarkdown(content)}</div>
                ${sourcesHtml}
            </div>`;

        chatMessages.appendChild(msgDiv);
        chatViewport.scrollTop = chatViewport.scrollHeight;
    }

    function appendLoadingMessage() {
        const id = 'loading-' + Date.now();
        const msgDiv = document.createElement('div');
        msgDiv.className = 'chat-bubble-row assistant';
        msgDiv.id = id;
        msgDiv.innerHTML = `
            <div class="chat-avatar"><i class="fa-solid fa-sparkles"></i></div>
            <div class="chat-bubble-content">
                <div class="loading-dots">
                    <span class="spinner"></span>
                    <span>Searching Knowledge Base & generating answer...</span>
                </div>
            </div>`;
        chatMessages.appendChild(msgDiv);
        chatViewport.scrollTop = chatViewport.scrollHeight;
        return id;
    }

    function removeMessage(id) {
        const elem = document.getElementById(id);
        if (elem) elem.remove();
    }

    // Markdown formatting helper
    function formatMarkdown(text) {
        if (!text) return '';
        let html = escapeHtml(text);
        html = html.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
        html = html.replace(/\*(.*?)\*/g, '<em>$1</em>');
        html = html.replace(/`(.*?)`/g, '<code>$1</code>');
        html = html.replace(/\n\n/g, '<br><br>');
        html = html.replace(/\n/g, '<br>');
        return html;
    }

    function escapeHtml(str) {
        return str.replace(/[&<>"']/g, (m) => ({
            '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#039;'
        }[m]));
    }

    // Modal Handling
    window.openSourceModal = (docName, page, chunkId, score, snippet) => {
        modalTitle.textContent = docName;
        modalMeta.innerHTML = `
            <div class="meta-item">
                <span class="meta-label">Location</span>
                <span class="meta-value">${page}</span>
            </div>
            <div class="meta-item">
                <span class="meta-label">Chunk ID</span>
                <span class="meta-value">${chunkId}</span>
            </div>
            ${score ? `
            <div class="meta-item">
                <span class="meta-label">Similarity</span>
                <span class="meta-value">${score}</span>
            </div>` : ''}
        `;
        modalContent.textContent = snippet || "No snippet preview available.";
        sourceModal.style.display = 'flex';
    };

    function closeModal() {
        sourceModal.style.display = 'none';
    }

    if (closeModalBtn) closeModalBtn.addEventListener('click', closeModal);
    if (modalDoneBtn) modalDoneBtn.addEventListener('click', closeModal);

    sourceModal.addEventListener('click', (e) => {
        if (e.target === sourceModal) closeModal();
    });

    // Copy modal text button
    if (modalCopyBtn) {
        modalCopyBtn.addEventListener('click', () => {
            const textToCopy = modalContent.textContent;
            navigator.clipboard.writeText(textToCopy).then(() => {
                const originalHtml = modalCopyBtn.innerHTML;
                modalCopyBtn.innerHTML = '<i class="fa-solid fa-check"></i> Copied!';
                setTimeout(() => {
                    modalCopyBtn.innerHTML = originalHtml;
                }, 2000);
            }).catch(err => {
                console.error('Failed to copy text: ', err);
            });
        });
    }

    // Press Escape to close modal
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' && sourceModal.style.display === 'flex') {
            closeModal();
        }
    });
});
