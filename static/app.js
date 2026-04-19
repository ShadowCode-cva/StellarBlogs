// Stellar Blog - Frontend State
const API_URL = '/api';
let state = {
    user: JSON.parse(localStorage.getItem('user')) || null,
    token: localStorage.getItem('token') || null,
    blogs: []
};

// Initialize app
document.addEventListener('DOMContentLoaded', () => {
    updateUI();
    fetchBlogs();
    
    // Simple Router
    window.showView = (view) => {
        document.getElementById('home-view').style.display = view === 'home' ? 'block' : 'none';
        document.getElementById('favorites-view').style.display = view === 'favorites' ? 'block' : 'none';
        if (view === 'favorites') fetchFavorites();
        if (view === 'home') fetchBlogs();
    };

    window.openModal = (id) => document.getElementById(id).classList.add('active');
    window.closeModal = (id) => document.getElementById(id).classList.remove('active');

    // Close modals on outside click
    window.onclick = (event) => {
        if (event.target.classList.contains('modal')) {
            event.target.classList.remove('active');
        }
    };
});

// UI Management
function updateUI() {
    const authLinks = document.getElementById('auth-links');
    const userLinks = document.getElementById('user-links');
    const welcomeText = document.getElementById('welcome-text');
    const authorBtn = document.getElementById('author-btn');

    if (state.token && state.user) {
        authLinks.style.display = 'none';
        userLinks.style.display = 'flex';
        userLinks.style.alignItems = 'center';
        userLinks.style.gap = '1.5rem';
        welcomeText.innerText = `Hi, ${state.user.username}`;
        authorBtn.style.display = state.user.role === 'author' ? 'block' : 'none';
    } else {
        authLinks.style.display = 'flex';
        userLinks.style.display = 'none';
    }
}

function openModal(id) {
    document.getElementById(id).style.display = 'flex';
}

function closeModal(id) {
    document.getElementById(id).style.display = 'none';
}

// Data Fetching
async function fetchBlogs(query = '') {
    const container = document.getElementById('blog-container');
    const url = query ? `${API_URL}/blogs/search?q=${encodeURIComponent(query)}` : `${API_URL}/blogs/`;
    
    try {
        const res = await fetch(url);
        const data = await res.json();
        state.blogs = data.blogs || [];
        renderBlogs();
    } catch (err) {
        console.error('Fetch error:', err);
        container.innerHTML = '<p class="error">Failed to load articles. Please check your connection.</p>';
    }
}

function renderBlogs() {
    const container = document.getElementById('blog-container');
    
    if (!state.blogs || state.blogs.length === 0) {
        container.innerHTML = '<div style="grid-column: 1/-1; text-align: center; padding: 4rem;"><h3>No stories found matching your criteria.</h3></div>';
        return;
    }

    container.innerHTML = state.blogs.map(blog => `
        <article class="blog-card" onclick="viewBlog('${blog._id}')">
            <div class="blog-meta">
                <span class="tag">${escapeHTML(blog.tags && blog.tags.length > 0 ? blog.tags[0] : 'General')}</span>
                <span>${new Date(blog.created_at).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })}</span>
            </div>
            <h3>${escapeHTML(blog.title)}</h3>
            <p>${escapeHTML(blog.content.length > 150 ? blog.content.substring(0, 150) + '...' : blog.content)}</p>
            <div class="blog-meta">
                <span style="color: var(--primary)">Read More →</span>
                <div class="interactions">
                    <span>❤️ ${blog.likes ? blog.likes.length : 0}</span>
                </div>
            </div>
        </article>
    `).join('');
}

// Form Handlers
async function handleLogin(e) {
    e.preventDefault();
    const formData = new FormData(e.target);
    const body = Object.fromEntries(formData);

    try {
        const res = await fetch(`${API_URL}/auth/login`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(body)
        });

        const data = await res.json();
        if (res.ok) {
            localStorage.setItem('token', data.token);
            localStorage.setItem('user', JSON.stringify(data.user));
            state.token = data.token;
            state.user = data.user;
            showToast('Logged in successfully!', 'success');
            closeModal('login-modal');
            updateUI();
            e.target.reset();
        } else {
            showToast(data.error || 'Login failed', 'error');
        }
    } catch (err) {
        showToast('Server error. Please try again.', 'error');
    }
}

async function handleSignup(e) {
    e.preventDefault();
    const formData = new FormData(e.target);
    const body = Object.fromEntries(formData);

    try {
        const res = await fetch(`${API_URL}/auth/signup`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(body)
        });

        const data = await res.json();
        if (res.ok) {
            showToast('Welcome aboard! You can now login.', 'success');
            closeModal('signup-modal');
            e.target.reset();
        } else {
            showToast(data.error || 'Signup failed', 'error');
        }
    } catch (err) {
        showToast('Server error. Please try again.', 'error');
    }
}

async function handleCreateBlog(e) {
    e.preventDefault();
    const formData = new FormData(e.target);
    const body = Object.fromEntries(formData);
    body.tags = body.tags ? body.tags.split(',').map(t => t.trim()).filter(t => t !== '') : [];

    try {
        const res = await fetch(`${API_URL}/blogs/`, {
            method: 'POST',
            headers: { 
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${state.token}`
            },
            body: JSON.stringify(body)
        });

        if (res.ok) {
            showToast('Blog published successfully!', 'success');
            closeModal('create-blog-modal');
            fetchBlogs();
            e.target.reset();
        } else {
            const data = await res.json();
            showToast(data.error || 'Failed to create blog', 'error');
        }
    } catch (err) {
        showToast('Server error. Please try again.', 'error');
    }
}

// Search & Navigation
let searchTimeout;
function handleSearch(e) {
    clearTimeout(searchTimeout);
    const query = e.target.value;
    
    searchTimeout = setTimeout(() => {
        fetchBlogs(query);
    }, 400);
}

function logout() {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    state.user = null;
    state.token = null;
    updateUI();
}

let currentBlogId = null;

async function viewBlog(id) {
    currentBlogId = id;
    openModal('blog-detail-modal');
    
    // Reset View
    document.getElementById('detail-title').innerText = 'Loading...';
    document.getElementById('detail-content').innerText = '';
    document.getElementById('comments-display').innerHTML = 'Loading comments...';
    
    try {
        const res = await fetch(`${API_URL}/blogs/${id}`);
        const data = await res.json();
        const blog = data.blog;
        
        document.getElementById('detail-title').innerText = blog.title;
        document.getElementById('detail-content').innerText = blog.content;
        document.getElementById('detail-date').innerText = new Date(blog.created_at).toLocaleDateString();
        document.getElementById('like-count').innerText = blog.likes ? blog.likes.length : 0;
        
        // Show/Hide Comment Form
        document.getElementById('comment-form-container').style.display = state.token ? 'block' : 'none';
        
        // Set up interactions
        document.getElementById('like-btn').onclick = () => toggleLike(id);
        document.getElementById('fav-btn').onclick = () => toggleFavorite(id);
        
        fetchComments(id);
    } catch (err) {
        console.error('Error loading blog details:', err);
    }
}

async function toggleLike(id) {
    if (!state.token) return showToast('Please login to like posts', 'error');
    try {
        const res = await fetch(`${API_URL}/interactions/like/${id}`, {
            method: 'POST',
            headers: { 'Authorization': `Bearer ${state.token}` }
        });
        const data = await res.json();
        if (res.ok) {
            document.getElementById('like-count').innerText = data.liked ? 
                parseInt(document.getElementById('like-count').innerText) + 1 :
                Math.max(0, parseInt(document.getElementById('like-count').innerText) - 1);
        }
    } catch (err) { console.error(err); }
}

async function toggleFavorite(id) {
    if (!state.token) return showToast('Please login to favorite posts', 'error');
    try {
        const res = await fetch(`${API_URL}/interactions/favorite/${id}`, {
            method: 'POST',
            headers: { 'Authorization': `Bearer ${state.token}` }
        });
        const data = await res.json();
        if (res.ok) showToast(data.message, 'success');
    } catch (err) { console.error(err); }
}

async function fetchComments(blogId) {
    try {
        const res = await fetch(`${API_URL}/comments/blog/${blogId}`);
        const data = await res.json();
        renderComments(data.comments);
    } catch (err) { console.error(err); }
}

function escapeHTML(str) {
    const p = document.createElement('p');
    p.textContent = str;
    return p.innerHTML;
}

function renderComments(comments, containerId = 'comments-display') {
    const container = document.getElementById(containerId);
    if (!comments || comments.length === 0) {
        if (containerId === 'comments-display') container.innerHTML = '<p style="color: var(--text-muted)">No comments yet. Be the first!</p>';
        return "";
    }

    const html = comments.map(comment => `
        <div class="comment" style="margin-bottom: 1.5rem; padding-left: 1rem; border-left: 1px solid var(--glass-border);">
            <div style="font-size: 0.8rem; color: var(--text-muted); margin-bottom: 0.4rem; display: flex; justify-content: space-between;">
                <span><strong>User</strong> • ${new Date(comment.created_at).toLocaleTimeString()}</span>
                <button onclick="handleCommentLike('${comment._id}')" style="background:none; border:none; color:var(--text-muted); cursor:pointer; font-size: 0.8rem; display: flex; align-items: center; gap: 4px;">
                    👍 ${comment.likes ? comment.likes.length : 0}
                </button>
            </div>
            <div style="margin-bottom: 0.6rem; font-size: 0.95rem;">${escapeHTML(comment.content)}</div>
            <div class="comment-actions">
                ${state.token ? `<button onclick="showReplyForm('${comment._id}')" style="background:none; border:none; color:var(--primary); cursor:pointer; font-size: 0.8rem; padding: 0;">Reply</button>` : ''}
            </div>
            <div id="reply-form-${comment._id}" style="display:none; margin-top: 1rem;">
                <textarea id="input-${comment._id}" placeholder="Write a reply..." rows="2" style="font-size: 0.9rem;"></textarea>
                <button onclick="handleAddComment('${comment._id}')" class="btn-primary" style="font-size: 0.75rem; padding: 0.3rem 0.8rem; margin-top: 0.5rem;">Post Reply</button>
            </div>
            <div id="replies-${comment._id}" style="margin-top: 1rem;">
                ${comment.replies ? renderComments(comment.replies, `replies-${comment._id}`) : ''}
            </div>
        </div>
    `).join('');

    if (containerId === 'comments-display') {
        container.innerHTML = html;
    }
    return html;
}

async function handleCommentLike(commentId) {
    if (!state.token) return showToast('Please login to like comments', 'error');
    try {
        const res = await fetch(`${API_URL}/comments/like/${commentId}`, {
            method: 'POST',
            headers: { 'Authorization': `Bearer ${state.token}` }
        });
        if (res.ok) {
            fetchComments(currentBlogId);
        }
    } catch (err) { console.error(err); }
}

async function fetchFavorites() {
    const container = document.getElementById('favorites-container');
    container.innerHTML = '<div style="grid-column: 1/-1; text-align: center;">Loading your favorites...</div>';
    
    try {
        const res = await fetch(`${API_URL}/interactions/favorites`, {
            headers: { 'Authorization': `Bearer ${state.token}` }
        });
        const data = await res.json();
        
        if (data.favorites && data.favorites.length > 0) {
            container.innerHTML = data.favorites.map(blog => `
                <article class="blog-card" onclick="viewBlog('${blog._id}')">
                    <div class="blog-meta">
                        <span class="tag">${blog.tags[0] || 'Saved'}</span>
                        <span>${new Date(blog.created_at).toLocaleDateString()}</span>
                    </div>
                    <h3>${blog.title}</h3>
                    <p>${blog.content.substring(0, 100)}...</p>
                    <div class="blog-meta">
                        <span style="color: var(--primary)">View Story →</span>
                    </div>
                </article>
            `).join('');
        } else {
            container.innerHTML = '<div style="grid-column: 1/-1; text-align: center; padding: 2rem;">You haven\'t saved any favorites yet. Start exploring!</div>';
        }
    } catch (err) { console.error(err); }
}

function openFavorites() {
    showView('favorites');
}

function showReplyForm(id) {
    const form = document.getElementById(`reply-form-${id}`);
    form.style.display = form.style.display === 'none' ? 'block' : 'none';
}

function togglePasswordVisibility(inputId, icon) {
    const input = document.getElementById(inputId);
    if (input.type === 'password') {
        input.type = 'text';
        icon.classList.remove('fa-eye');
        icon.classList.add('fa-eye-slash');
    } else {
        input.type = 'password';
        icon.classList.remove('fa-eye-slash');
        icon.classList.add('fa-eye');
    }
}

function showToast(message, type = 'success') {
    const container = document.getElementById('toast-container');
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    
    const icon = type === 'success' ? 'fa-check-circle' : 'fa-exclamation-circle';
    const color = type === 'success' ? 'var(--primary)' : 'var(--accent)';
    
    toast.innerHTML = `
        <i class="fas ${icon}" style="color: ${color}"></i>
        <span>${message}</span>
    `;
    
    container.appendChild(toast);
    
    setTimeout(() => {
        toast.style.opacity = '0';
        toast.style.transform = 'translateY(20px)';
        toast.style.transition = 'all 0.5s ease';
        setTimeout(() => toast.remove(), 500);
    }, 4000);
}

async function handleAddComment(parentId = null) {
    const inputId = parentId ? `input-${parentId}` : 'main-comment-input';
    const input = document.getElementById(inputId);
    const content = input.value.trim();
    
    if (!content) return;

    try {
        const res = await fetch(`${API_URL}/comments/`, {
            method: 'POST',
            headers: { 
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${state.token}`
            },
            body: JSON.stringify({
                blog_id: currentBlogId,
                content: content,
                parent_id: parentId
            })
        });

        if (res.ok) {
            input.value = '';
            if (parentId) document.getElementById(`reply-form-${parentId}`).style.display = 'none';
            fetchComments(currentBlogId);
        } else {
            const data = await res.json();
            showToast(data.error, 'error');
        }
    } catch (err) { console.error(err); }
}
