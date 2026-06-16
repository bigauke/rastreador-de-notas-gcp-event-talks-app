document.addEventListener('DOMContentLoaded', () => {
    // DOM Elements
    const refreshBtn = document.getElementById('refresh-btn');
    const spinner = document.getElementById('spinner');
    const dateList = document.getElementById('date-list');
    const dateCount = document.getElementById('date-count');
    const activeDateTitle = document.getElementById('active-date-title');
    const activeDateRaw = document.getElementById('active-date-raw');
    const updatesContainer = document.getElementById('updates-container');
    const tweetTextarea = document.getElementById('tweet-textarea');
    const charCount = document.getElementById('char-count');
    const tweetBtn = document.getElementById('tweet-btn');
    const composerDateTag = document.getElementById('composer-date-tag');
    const includeLinkToggle = document.getElementById('include-link-toggle');
    const shareAllBtn = document.getElementById('share-all-btn');

    // State
    let releaseNotes = [];
    let selectedEntry = null;
    let selectedUpdateText = '';
    const releaseNotesDocUrl = 'https://cloud.google.com/bigquery/docs/release-notes';

    // Translations for UI Badge types
    const typeTranslations = {
        'feature': 'Recurso',
        'change': 'Alteração',
        'deprecated': 'Depreciado',
        'removed': 'Removido',
        'release': 'Lançamento'
    };

    function translateType(type) {
        const lower = type.toLowerCase();
        for (const [key, val] of Object.entries(typeTranslations)) {
            if (lower.includes(key)) return val;
        }
        return type;
    }

    // Fetch Release Notes from Flask API
    async function fetchNotes(isRefresh = false) {
        setLoadingState(true);
        try {
            const response = await fetch('/api/release-notes');
            const result = await response.json();
            
            if (result.success && result.data && result.data.length > 0) {
                releaseNotes = result.data;
                renderDateList(releaseNotes);
                // Select the first entry by default
                selectEntry(releaseNotes[0]);
            } else {
                renderError(result.error || 'Falha ao buscar as notas de lançamento.');
            }
        } catch (error) {
            console.error('Error fetching release notes:', error);
            renderError('Erro de conexão. Verifique se o servidor Flask está rodando.');
        } finally {
            setLoadingState(false);
        }
    }

    // Set Loading UI state
    function setLoadingState(isLoading) {
        if (isLoading) {
            spinner.classList.add('spinning');
            refreshBtn.disabled = true;
            if (dateList.querySelector('.loading-placeholder') === null) {
                dateList.innerHTML = `
                    <div class="loading-placeholder">
                        <div class="skeleton-line" style="width: 80%;"></div>
                        <div class="skeleton-line" style="width: 90%;"></div>
                        <div class="skeleton-line" style="width: 70%;"></div>
                    </div>
                `;
            }
        } else {
            spinner.classList.remove('spinning');
            refreshBtn.disabled = false;
        }
    }

    // Render Sidebar Dates
    function renderDateList(entries) {
        dateList.innerHTML = '';
        dateCount.textContent = `${entries.length} Data${entries.length !== 1 ? 's' : ''}`;
        
        entries.forEach((entry, index) => {
            const item = document.createElement('div');
            item.className = 'date-item';
            if (selectedEntry && selectedEntry.id === entry.id) {
                item.classList.add('active');
            }
            
            // Format updated timestamp in pt-BR
            let timeStr = '';
            if (entry.updated) {
                try {
                    const dateObj = new Date(entry.updated);
                    timeStr = dateObj.toLocaleDateString('pt-BR', { 
                        year: 'numeric', 
                        month: 'short', 
                        day: 'numeric' 
                    });
                } catch (e) {
                    timeStr = entry.updated;
                }
            }
            
            item.innerHTML = `
                <div class="date-item-title">${escapeHtml(entry.title || 'Data Desconhecida')}</div>
                <div class="date-item-meta">${escapeHtml(timeStr)}</div>
            `;
            
            item.addEventListener('click', () => {
                // Remove active class from previous items
                document.querySelectorAll('.date-item').forEach(el => el.classList.remove('active'));
                item.classList.add('active');
                selectEntry(entry);
            });
            
            dateList.appendChild(item);
        });
    }

    // Select Entry and render updates
    function selectEntry(entry) {
        selectedEntry = entry;
        activeDateTitle.textContent = entry.title || 'Detalhes do Lançamento';
        
        // Format raw update timestamp in pt-BR
        let rawDateText = 'Sem informações de data';
        if (entry.updated) {
            try {
                const dateObj = new Date(entry.updated);
                rawDateText = dateObj.toLocaleString('pt-BR');
            } catch (e) {
                rawDateText = entry.updated;
            }
        }
        activeDateRaw.textContent = rawDateText;
        composerDateTag.textContent = entry.title || 'Data Selecionada';
        
        // Show the summary share button
        shareAllBtn.style.display = 'inline-flex';

        // Parse HTML content to extract individual updates
        const parsedUpdates = parseUpdatesFromContent(entry.content);
        renderUpdates(parsedUpdates, entry.title);
        
        // Clear selection text on date change
        selectedUpdateText = '';
        updateComposer();
    }

    // Parse Atom entry HTML content into structured list of updates (e.g. grouped by <h3> tags)
    function parseUpdatesFromContent(htmlContent) {
        if (!htmlContent) return [];
        
        const parser = new DOMParser();
        const doc = parser.parseFromString(htmlContent, 'text/html');
        const updates = [];
        
        let currentType = null;
        let currentHTML = '';
        
        // Traverse top-level elements of parsed HTML
        const childNodes = Array.from(doc.body.childNodes);
        
        childNodes.forEach((node) => {
            if (node.nodeType === Node.ELEMENT_NODE && node.tagName.toLowerCase() === 'h3') {
                // Save previous parsed update if exists
                if (currentType) {
                    updates.push({
                        type: currentType,
                        content: currentHTML.trim()
                    });
                }
                currentType = node.textContent.trim();
                currentHTML = '';
            } else {
                // Append node content
                if (node.nodeType === Node.ELEMENT_NODE) {
                    currentHTML += node.outerHTML;
                } else if (node.nodeType === Node.TEXT_NODE) {
                    currentHTML += node.textContent;
                }
            }
        });
        
        // Add final segment
        if (currentType) {
            updates.push({
                type: currentType,
                content: currentHTML.trim()
            });
        }
        
        // Fallback if no <h3> tags found
        if (updates.length === 0 && htmlContent.trim()) {
            updates.push({
                type: 'Release',
                content: htmlContent.trim()
            });
        }
        
        return updates;
    }

    // Render Updates in main details container
    function renderUpdates(updates, dateTitle) {
        updatesContainer.innerHTML = '';
        
        if (updates.length === 0) {
            updatesContainer.innerHTML = `
                <div class="empty-state">
                    <h3>Sem detalhes disponíveis</h3>
                    <p>Esta entrada não contém nenhum texto de atualização legível.</p>
                </div>
            `;
            return;
        }
        
        updates.forEach((update) => {
            const card = document.createElement('div');
            const lowerType = update.type.toLowerCase();
            
            // Map type to design token classes
            let typeClass = 'change';
            if (lowerType.includes('feature')) typeClass = 'feature';
            else if (lowerType.includes('deprecated')) typeClass = 'deprecated';
            else if (lowerType.includes('remove') || lowerType.includes('delete')) typeClass = 'removed';
            
            card.className = `update-card ${typeClass}`;
            
            // Extract plain text for X sharing
            const plainText = getPlainTextFromHtml(update.content);
            
            card.innerHTML = `
                <div class="update-card-header">
                    <span class="type-badge ${typeClass}">${escapeHtml(translateType(update.type))}</span>
                    <div class="card-actions">
                        <button class="btn-card-action tweet-select-btn" title="Enviar atualização para o rascunho de Tweet">
                            <svg class="x-logo" viewBox="0 0 24 24" fill="currentColor" xmlns="http://www.w3.org/2005/svg" style="width:12px;height:12px;">
                                <path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z"/>
                            </svg>
                            <span>Rascunho</span>
                        </button>
                    </div>
                </div>
                <div class="update-card-content">
                    ${update.content}
                </div>
            `;
            
            // Add event listener to the specific "Tweet" draft button
            card.querySelector('.tweet-select-btn').addEventListener('click', () => {
                selectTextForComposer(plainText, update.type, dateTitle);
                
                // Visual feedback - temporary active effect
                card.style.borderColor = 'var(--accent-twitter)';
                setTimeout(() => {
                    card.style.borderColor = 'var(--border-glass)';
                }, 1000);
            });
            
            updatesContainer.appendChild(card);
        });
    }

    // Helper to strip tags and format HTML into standard text
    function getPlainTextFromHtml(html) {
        const temp = document.createElement('div');
        temp.innerHTML = html;
        
        // Custom formatting for lists so they render nicely as plain text
        const listItems = temp.querySelectorAll('li');
        listItems.forEach(li => {
            li.textContent = `• ${li.textContent.trim()}\n`;
        });
        
        let text = temp.innerText || temp.textContent || '';
        
        // Clean up redundant line breaks
        text = text.replace(/\n\s*\n/g, '\n').trim();
        return text;
    }

    // Select text content and push to Composer input
    function selectTextForComposer(text, type, date) {
        selectedUpdateText = text;
        composerDateTag.textContent = date;
        
        updateComposer();
        
        // Focus the composer on desktop/large screens
        if (window.innerWidth > 768) {
            tweetTextarea.focus();
        }
    }

    // Compose Tweet Content based on parameters and update UI controls
    function updateComposer() {
        if (!selectedUpdateText) {
            tweetTextarea.value = '';
            tweetTextarea.placeholder = 'Selecione uma atualização dos cartões para criar um rascunho de Tweet...';
            tweetBtn.disabled = true;
            charCount.textContent = '0';
            charCount.className = 'character-counter';
            return;
        }

        const dateHeader = selectedEntry ? selectedEntry.title : '';
        const linkStr = includeLinkToggle.checked ? `\n\nNotas de lançamento: ${releaseNotesDocUrl}` : '';
        
        // Base draft structure
        let draft = `Atualização do BigQuery [${dateHeader}]:\n\n${selectedUpdateText}`;
        
        // If the draft exceeds the maximum twitter length (accounting for links), we truncate it nicely
        const maxTweetLength = 280;
        const linkLength = linkStr.length;
        const availableTextLength = maxTweetLength - 30 - linkLength; // Buffer of 30 characters for headers
        
        // Build the full draft
        let fullDraft = `${draft}${linkStr}`;
        
        tweetTextarea.value = fullDraft;
        handleCharCount();
    }

    // Handle Live character count
    function handleCharCount() {
        const len = tweetTextarea.value.length;
        charCount.textContent = len;
        
        if (len > 280) {
            charCount.className = 'character-counter danger';
            tweetBtn.disabled = true;
        } else if (len > 250) {
            charCount.className = 'character-counter warning';
            tweetBtn.disabled = false;
        } else {
            charCount.className = 'character-counter';
            tweetBtn.disabled = len === 0;
        }
    }

    // Open Web Intent in a new tab to Tweet
    function postTweet() {
        const text = tweetTextarea.value.trim();
        if (text.length === 0 || text.length > 280) return;
        
        const url = `https://twitter.com/intent/tweet?text=${encodeURIComponent(text)}`;
        window.open(url, '_blank');
    }

    // Handle formatting error state
    function renderError(message) {
        dateList.innerHTML = `<div style="color: var(--accent-red); padding: 12px; font-size: 0.85rem;">${escapeHtml(message)}</div>`;
        updatesContainer.innerHTML = `
            <div class="empty-state">
                <svg class="empty-icon" style="color: var(--accent-red);" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2005/svg">
                    <path d="M12 2C6.48 2 2 6.48 2 12C2 17.52 6.48 22 12 22C17.52 22 22 17.52 22 12C22 6.48 17.52 2 12 2ZM13 17H11V15H13V17ZM13 13H11V7H13V13Z" fill="currentColor"/>
                </svg>
                <h3>Falha ao carregar as notas de lançamento</h3>
                <p>${escapeHtml(message)}</p>
                <button id="retry-btn" class="btn btn-secondary">Tentar Novamente</button>
            </div>
        `;
        
        const retryBtn = document.getElementById('retry-btn');
        if (retryBtn) {
            retryBtn.addEventListener('click', () => fetchNotes(true));
        }
    }

    // General Summary Tweet Creator (Drafts summary of the entire date)
    function generateDaySummaryTweet() {
        if (!selectedEntry) return;
        
        const updates = parseUpdatesFromContent(selectedEntry.content);
        if (updates.length === 0) return;
        
        let summaryText = '';
        updates.forEach(u => {
            summaryText += `- ${translateType(u.type)}: ${u.content.replace(/<[^>]*>/g, '').substring(0, 40).trim()}...\n`;
        });
        
        selectedUpdateText = `Resumo das atualizações:\n${summaryText.trim()}`;
        updateComposer();
    }

    // Escape HTML helper
    function escapeHtml(text) {
        if (!text) return '';
        const map = {
            '&': '&amp;',
            '<': '&lt;',
            '>': '&gt;',
            '"': '&quot;',
            "'": '&#039;'
        };
        return text.replace(/[&<>"']/g, function(m) { return map[m]; });
    }

    // Event Listeners
    refreshBtn.addEventListener('click', () => fetchNotes(true));
    tweetTextarea.addEventListener('input', handleCharCount);
    tweetBtn.addEventListener('click', postTweet);
    includeLinkToggle.addEventListener('change', updateComposer);
    shareAllBtn.addEventListener('click', generateDaySummaryTweet);

    // Initial Fetch
    fetchNotes();
});
