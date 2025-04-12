document.addEventListener('DOMContentLoaded', function() {
    // Sidebar toggle functionality
    const sidebarCollapse = document.getElementById('sidebarCollapse');
    const sidebar = document.getElementById('sidebar');
    const content = document.getElementById('content');
    const header = document.getElementById('header');
    
    if (sidebarCollapse) {
        sidebarCollapse.addEventListener('click', function() {
            sidebar.classList.toggle('active');
            
            if (sidebar.classList.contains('active')) {
                content.style.marginLeft = '0';
                content.style.width = '100%';
                header.style.marginLeft = '0';
                header.style.width = '100%';
            } else {
                content.style.marginLeft = 'var(--sidebar-width)';
                content.style.width = 'calc(100% - var(--sidebar-width))';
                header.style.marginLeft = 'var(--sidebar-width)';
                header.style.width = 'calc(100% - var(--sidebar-width))';
            }
        });
    }
    
    // Add active class to current page in sidebar
    const currentLocation = window.location.pathname;
    const menuItems = document.querySelectorAll('#sidebar a');
    
    menuItems.forEach(function(item) {
        if (item.getAttribute('href') === currentLocation) {
            item.classList.add('active-nav-link');
            
            // If it's in a submenu, expand the parent
            const parent = item.closest('ul.collapse');
            if (parent) {
                parent.classList.add('show');
                const parentToggle = document.querySelector('[href="#' + parent.id + '"]');
                if (parentToggle) {
                    parentToggle.setAttribute('aria-expanded', 'true');
                    parentToggle.classList.add('active-nav-link');
                }
            }
        }
    });
});
