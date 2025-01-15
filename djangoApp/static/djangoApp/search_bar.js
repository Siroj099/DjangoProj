// Global variables to track state
let currentQuery = '';
let currentPage = 1;
let searchTimer;

// Initialize when document loads
document.addEventListener('DOMContentLoaded', function() {

    const searchInput = document.getElementById('searchInput');
    const searchResults = document.getElementById('searchResults');    
    const searchContainer = document.getElementById('createTicketBtn');
    
    
    // Initial load of tickets with pagination
    liveSearch(currentQuery, currentPage);

    // Search input handler
    searchInput.addEventListener('input', function() {
        clearTimeout(searchTimer);
        currentQuery = this.value;
        currentPage = 1;
        
        searchTimer = setTimeout(() => {
            liveSearch(currentQuery, currentPage);
        }, 500);
    });

    if (createTicketBtn) {
        createTicketBtn.addEventListener('click', openCreateTicketModal);
    } else {
        console.error('Create Ticket button not found!')
    }

});

function liveSearch(query, page = 1) {
    fetch(`search/?query=${encodeURIComponent(query)}&page=${page}`, {
        headers: {
            'X-Requested-With': 'XMLHttpRequest',
            'Accept': 'application/json'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (!data.success) {
            throw new Error(data.error);
        }
        
        const searchResults = document.getElementById('searchResults');
        searchResults.innerHTML = '';
        
        if (data.count === 0) {
            searchResults.innerHTML = '<p class="text-gray-500 p-4">No tickets found</p>';
            document.getElementById('paginator').innerHTML = '';
            return;
        }

        searchResults.innerHTML = data.html; 
        updatePagination(data.pagination);
    })
    .catch(error => {
        console.error('Error:', error);
        document.getElementById('searchResults').innerHTML = 
            '<p class="text-red-500 p-4">Error loading results: ' + error.message + '</p>';
        document.getElementById('paginator').innerHTML = '';
    });
}

function updatePagination(paginationData) {
    const template = `
        <div class="flex justify-center my-4">
            <div class="pagination flex items-center space-x-2">
                ${paginationData.has_previous ? `
                    <a href="javascript:void(0)" onclick="changePage(1)" 
                       class="px-3 py-2 rounded border hover:bg-blue-100">First</a>
                    <a href="javascript:void(0)" onclick="changePage(${paginationData.current_page - 1})" 
                       class="px-3 py-2 rounded border hover:bg-blue-100">Previous</a>
                ` : ''}

                ${generatePageNumbers(paginationData)}

                ${paginationData.has_next ? `
                    <a href="javascript:void(0)" onclick="changePage(${paginationData.current_page + 1})" 
                       class="px-3 py-2 rounded border hover:bg-blue-100">Next</a>
                    <a href="javascript:void(0)" onclick="changePage(${paginationData.total_pages})" 
                       class="px-3 py-2 rounded border hover:bg-blue-100">Last</a>
                ` : ''}
            </div>
        </div>
    `;
    document.getElementById('paginator').innerHTML = template;
}

function generatePageNumbers(paginationData) {
    let pages = '';
    const current = paginationData.current_page;
    const total = paginationData.total_pages;
    
    for (let i = 1; i <= total; i++) {
        if (i === current) {
            pages += `<span class="px-3 py-2 rounded border bg-blue-500 text-white">${i}</span>`;
        } else if (
            i === 1 || 
            i === total || 
            (i >= current - 2 && i <= current + 2)
        ) {
            pages += `<a href="javascript:void(0)" onclick="changePage(${i})" 
                     class="px-3 py-2 rounded border hover:bg-blue-100">${i}</a>`;
        } else if (
            i === current - 3 || 
            i === current + 3
        ) {
            pages += `<span class="px-3 py-2">...</span>`;
        }
    }
    return pages;
}

function changePage(page) {
    currentPage = page;
    liveSearch(currentQuery, currentPage);
}

//function to open the modal
function openCreateTicketModal() {
    console.log("Opening modal...");
    const modal = document.createElement('div');
    modal.className = 'fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full flex items-center justify-center';
    modal.id = 'createTicketModal';
    
    modal.innerHTML = `
        <div class="relative bg-white rounded-lg shadow-xl p-8 m-4 max-w-xl w-full">
            <div class="flex justify-between items-center mb-4">
                <h3 class="text-xl font-bold">Create New Ticket</h3>
                <button onclick="closeCreateTicketModal()" class="text-gray-600 hover:text-gray-800">&times;</button>
            </div>
            <form id="createTicketForm" class="space-y-4">
                <div>
                    <label class="block text-sm font-medium text-gray-700">Title</label>
                    <input type="text" id="ticketTitle" required
                        class="mt-1 block w-full rounded-md border-gray-300 shadow-sm p-2 border">
                </div>
                <div>
                    <label class="block text-sm font-medium text-gray-700">Description</label>
                    <textarea id="ticketDescription" required
                        class="mt-1 block w-full rounded-md border-gray-300 shadow-sm p-2 border"
                        rows="4"></textarea>
                </div>
                <div>
                    <label class="block text-sm font-medium text-gray-700">Author Name (First and Last Name)</label>
                    <input type="text" id="ticketAuthor" required
                        placeholder="e.g., John Cena"
                        class="mt-1 block w-full rounded-md border-gray-300 shadow-sm p-2 border"
                        rows="1"></textarea>
                </div>
                <div class="flex justify-end space-x-2">
                    <button type="button" onclick="closeCreateTicketModal()"
                        class="px-4 py-2 bg-gray-200 text-gray-800 rounded hover:bg-gray-300">
                        Cancel
                    </button>
                    <button type="submit"
                        class="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600">
                        Create Ticket
                    </button>
                </div>
            </form>
        </div>
    `;
    
    document.body.appendChild(modal);
    
    // Add submit handler
    document.getElementById('createTicketForm').addEventListener('submit', handleCreateTicket);
}

function closeCreateTicketModal() {
    const modal = document.getElementById('createTicketModal');
    if (modal) {
        modal.remove();
    }
}

async function handleCreateTicket(e) {
    e.preventDefault();
    
    const title = document.getElementById('ticketTitle').value;
    const description = document.getElementById('ticketDescription').value;
    const author = document.getElementById('ticketAuthor').value;

    const csrftoken = getCookie('csrftoken');

    try {
        const response = await fetch('create_ticket/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-Requested-With': 'XMLHttpRequest',
                'X-CSRFToken': csrftoken,
            },
            body: JSON.stringify({
                title: title,
                description: description,
                author: author,
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            closeCreateTicketModal();
            // Refresh the ticket list

            currentQuery = '';
            currentPage = 1;

            // clearing search input
            const searchInput = document.getElementById('searchInput');
            if (searchInput) {
                searchInput.value = '';
            }
            await liveSearch('', 1);

        } else {
            alert('Error creating ticket: ' + data.error);
        }
    } catch (error) {
        console.error('Error:', error);
        alert('Error creating ticket. Please try again.');
    }
}

async function handleAddComment(ticketId){
    const commentAuthor = document.getElementById(`commentAuthor-${ticketId}`).value;
    const commentDescription = document.getElementById(`commentDescription-${ticketId}`).value;

    const csrftoken = getCookie('csrftoken');

    try {
        const response = await fetch('create_comment/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-Requested-With': 'XMLHttpRequest',
                'X-CSRFToken': csrftoken,
            },
            body: JSON.stringify({
                comment: commentDescription,
                author: commentAuthor,
                ticketId: ticketId,
            })
        });
        
        const data = await response.json();
        
        if (data.success && data.ticketSection) {

            hideAddComment(ticketId);
            await liveSearch('', 1);
        }
    } catch (error) {
        console.error('Error:', error);
        alert('Error creating comment. Please try again.');
    }
}

async function handleAddReply(ticketId, commentId) {
    const replyAuthor = document.getElementById(`replyAuthor-${commentId}`).value;
    const replyDescription = document.getElementById(`replyDescription-${commentId}`).value;
    
    if (!replyAuthor || !replyDescription) {
        alert('Please fill in both author name and reply description');
            return;
    }
    
    const csrftoken = getCookie('csrftoken');
    try {
        const response = await fetch('create_reply/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-Requested-With': 'XMLHttpRequest',
                'X-CSRFToken': csrftoken,
            },
            body: JSON.stringify({
                reply: replyDescription,
                author: replyAuthor,
                ticketId: ticketId, 
                commentId: commentId, 
            }),
        });
    
        const data = await response.json();
    
        if (data.success) {
            // Clear Add reply fields
            document.getElementById(`replyAuthor-${commentId}`).value = '';
            document.getElementById(`replyDescription-${commentId}`).value = '';
            hideAddReply(commentId);
                
            await liveSearch('', 1); // Refresh the comments or replies view
        } else {
            alert('Error creating reply: ' + data.error);
        }
    } catch (error) {
        console.error('Error:', error);
        alert('Error creating reply. Please try again.');
    }
}

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

function attachEventListeners(ticketId) {
    const newCommentForm = document.querySelector(`#ticketForm-${ticketId} form`);
    if (newCommentForm) {
        newCommentForm.addEventListener('submit', (e) => {
            e.preventDefault();
            handleAddComment(ticketId);
        });
    }
}
