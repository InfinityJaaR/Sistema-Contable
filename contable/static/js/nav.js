function toggleSidebar() {
    const sidebar = document.getElementById('sidebar');
    const content = document.getElementById('content');
    const toggleBtn = document.querySelector('.toggle-btn');
    sidebar.classList.toggle('collapsed');
    content.classList.toggle('expanded');
    
    if (sidebar.classList.contains('collapsed')) {
        toggleBtn.innerHTML = '☰'; // Right-pointing angle bracket
    } else {
        toggleBtn.innerHTML = '☰'; // Left-pointing angle bracket
    }
}