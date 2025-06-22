// Mobile optimizations and touch interactions for Gitako Farm Management

document.addEventListener('DOMContentLoaded', function() {
    initMobileOptimizations();
});

function initMobileOptimizations() {
    // Check if we're on mobile
    const isMobile = window.innerWidth <= 768;
    
    if (isMobile) {
        setupMobileNavigation();
        setupTouchGestures();
        setupMobileTables();
        setupMobileForms();
        setupQuickActions();
        setupPullToRefresh();
    }
    
    // Always setup responsive features
    setupResponsiveCharts();
    setupVirtualKeyboard();
    setupTouchOptimizations();
}

// Mobile Navigation Setup
function setupMobileNavigation() {
    // Create mobile navigation toggle
    const mobileNavToggle = document.createElement('button');
    mobileNavToggle.className = 'mobile-nav-toggle';
    mobileNavToggle.innerHTML = '<i class="material-icons">menu</i>';
    mobileNavToggle.setAttribute('aria-label', 'Toggle navigation');
    
    // Create mobile navigation bar
    const mobileNav = document.createElement('div');
    mobileNav.className = 'mobile-nav d-lg-none';
    mobileNav.innerHTML = `
        <div class="d-flex align-items-center justify-content-between">
            <div class="d-flex align-items-center">
                ${mobileNavToggle.outerHTML}
                <span class="navbar-brand mb-0">Gitako Farm</span>
            </div>
            <div class="mobile-nav-actions">
                <button class="btn btn-link text-white p-2" onclick="showSearchModal()">
                    <i class="material-icons">search</i>
                </button>
                <button class="btn btn-link text-white p-2" onclick="showNotifications()">
                    <i class="material-icons">notifications</i>
                </button>
            </div>
        </div>
    `;
    
    // Insert mobile nav at the top
    const mainContent = document.querySelector('.main-content');
    if (mainContent) {
        mainContent.insertBefore(mobileNav, mainContent.firstChild);
    }
    
    // Create overlay for sidebar
    const overlay = document.createElement('div');
    overlay.className = 'sidebar-overlay';
    document.body.appendChild(overlay);
    
    // Setup event listeners
    const toggleBtn = document.querySelector('.mobile-nav-toggle');
    const sidebar = document.querySelector('.sidebar');
    
    if (toggleBtn && sidebar) {
        toggleBtn.addEventListener('click', () => {
            sidebar.classList.toggle('show');
            overlay.classList.toggle('show');
            document.body.style.overflow = sidebar.classList.contains('show') ? 'hidden' : '';
        });
        
        overlay.addEventListener('click', () => {
            sidebar.classList.remove('show');
            overlay.classList.remove('show');
            document.body.style.overflow = '';
        });
    }
}

// Touch Gestures Setup
function setupTouchGestures() {
    let startX, startY, currentX, currentY;
    let isSwipeActive = false;
    
    // Swipe to navigate
    document.addEventListener('touchstart', (e) => {
        startX = e.touches[0].clientX;
        startY = e.touches[0].clientY;
        isSwipeActive = true;
    }, { passive: true });
    
    document.addEventListener('touchmove', (e) => {
        if (!isSwipeActive) return;
        
        currentX = e.touches[0].clientX;
        currentY = e.touches[0].clientY;
        
        const diffX = currentX - startX;
        const diffY = currentY - startY;
        
        // Horizontal swipe detection
        if (Math.abs(diffX) > Math.abs(diffY) && Math.abs(diffX) > 50) {
            if (diffX > 0 && startX < 50) {
                // Swipe right from left edge - open sidebar
                document.querySelector('.sidebar')?.classList.add('show');
                document.querySelector('.sidebar-overlay')?.classList.add('show');
            } else if (diffX < 0 && startX > window.innerWidth - 50) {
                // Swipe left from right edge - could trigger other actions
                handleRightEdgeSwipe();
            }
        }
    }, { passive: true });
    
    document.addEventListener('touchend', () => {
        isSwipeActive = false;
    }, { passive: true });
    
    // Double tap to zoom (for charts and images)
    let lastTap = 0;
    document.addEventListener('touchend', (e) => {
        const currentTime = new Date().getTime();
        const tapLength = currentTime - lastTap;
        
        if (tapLength < 500 && tapLength > 0) {
            // Double tap detected
            const target = e.target.closest('.chart-container, .image-container');
            if (target) {
                toggleZoom(target);
            }
        }
        lastTap = currentTime;
    });
}

// Mobile Tables Setup
function setupMobileTables() {
    const tables = document.querySelectorAll('.table');
    
    tables.forEach(table => {
        if (!table.closest('.table-responsive')) {
            const wrapper = document.createElement('div');
            wrapper.className = 'table-responsive';
            table.parentNode.insertBefore(wrapper, table);
            wrapper.appendChild(table);
        }
        
        // Convert to mobile-friendly format if needed
        if (window.innerWidth <= 768) {
            convertToMobileTable(table);
        }
    });
}

function convertToMobileTable(table) {
    const headers = Array.from(table.querySelectorAll('thead th')).map(th => th.textContent.trim());
    const rows = table.querySelectorAll('tbody tr');
    
    rows.forEach(row => {
        const cells = row.querySelectorAll('td');
        cells.forEach((cell, index) => {
            if (headers[index]) {
                cell.setAttribute('data-label', headers[index]);
            }
        });
    });
    
    table.classList.add('mobile-table');
}

// Mobile Forms Setup
function setupMobileForms() {
    const forms = document.querySelectorAll('form');
    
    forms.forEach(form => {
        // Add mobile-friendly classes
        form.classList.add('mobile-form');
        
        // Handle form submission with offline support
        form.addEventListener('submit', handleMobileFormSubmit);
        
        // Setup better input handling
        const inputs = form.querySelectorAll('input, textarea, select');
        inputs.forEach(input => {
            setupMobileInput(input);
        });
    });
}

function setupMobileInput(input) {
    // Prevent zoom on iOS
    if (input.type !== 'file') {
        input.style.fontSize = '16px';
    }
    
    // Add floating labels for better UX
    if (input.type !== 'hidden' && input.type !== 'submit' && input.type !== 'button') {
        wrapInputWithFloatingLabel(input);
    }
    
    // Setup auto-save for long forms
    if (input.form && input.form.classList.contains('auto-save')) {
        input.addEventListener('change', debounce(autoSaveForm, 1000));
    }
}

function wrapInputWithFloatingLabel(input) {
    if (input.closest('.floating-label')) return;
    
    const wrapper = document.createElement('div');
    wrapper.className = 'floating-label';
    
    const label = input.previousElementSibling?.tagName === 'LABEL' ? 
                  input.previousElementSibling : 
                  input.parentNode.querySelector(`label[for="${input.id}"]`);
    
    if (label) {
        input.parentNode.insertBefore(wrapper, input);
        wrapper.appendChild(input);
        wrapper.appendChild(label);
        
        // Add focus/blur handlers
        input.addEventListener('focus', () => wrapper.classList.add('focused'));
        input.addEventListener('blur', () => {
            wrapper.classList.toggle('focused', input.value !== '');
        });
        
        // Initial state
        if (input.value !== '') {
            wrapper.classList.add('focused');
        }
    }
}

function handleMobileFormSubmit(e) {
    const form = e.target;
    
    // Show loading state
    const submitBtn = form.querySelector('button[type="submit"], input[type="submit"]');
    if (submitBtn) {
        const originalText = submitBtn.textContent || submitBtn.value;
        submitBtn.disabled = true;
        submitBtn.innerHTML = '<i class="material-icons spin">refresh</i> Submitting...';
        
        // Restore button after timeout
        setTimeout(() => {
            submitBtn.disabled = false;
            submitBtn.textContent = originalText;
        }, 3000);
    }
    
    // Handle offline form submission
    if (!navigator.onLine) {
        e.preventDefault();
        handleOfflineFormSubmission(form);
    }
}

function handleOfflineFormSubmission(form) {
    const formData = new FormData(form);
    const data = {};
    
    for (let [key, value] of formData.entries()) {
        data[key] = value;
    }
    
    // Save to offline storage
    if (window.offlineManager) {
        window.offlineManager.saveOfflineData('forms', {
            formAction: form.action,
            formMethod: form.method,
            formData: data
        });
        
        showNotification('Form saved offline. Will sync when connected.', 'info');
    }
}

// Quick Actions Setup
function setupQuickActions() {
    const quickActions = document.createElement('div');
    quickActions.className = 'quick-actions d-lg-none';
    quickActions.innerHTML = `
        <button class="fab" onclick="toggleFabMenu()" aria-label="Quick actions">
            <i class="material-icons">add</i>
        </button>
        <div class="fab-menu" id="fabMenu">
            <button class="fab" onclick="quickAddActivity()" aria-label="Add activity">
                <i class="material-icons">assignment</i>
            </button>
            <button class="fab" onclick="quickAddInventory()" aria-label="Add inventory">
                <i class="material-icons">inventory</i>
            </button>
            <button class="fab" onclick="quickViewCalendar()" aria-label="View calendar">
                <i class="material-icons">event</i>
            </button>
        </div>
    `;
    
    document.body.appendChild(quickActions);
}

function toggleFabMenu() {
    const menu = document.getElementById('fabMenu');
    const mainFab = document.querySelector('.quick-actions .fab:first-child i');
    
    menu.classList.toggle('show');
    mainFab.textContent = menu.classList.contains('show') ? 'close' : 'add';
}

// Pull to Refresh Setup
function setupPullToRefresh() {
    let startY = 0;
    let pullDistance = 0;
    let isRefreshing = false;
    
    const refreshThreshold = 80;
    const maxPullDistance = 120;
    
    const pullToRefreshElement = document.createElement('div');
    pullToRefreshElement.className = 'pull-to-refresh';
    pullToRefreshElement.innerHTML = `
        <div class="pull-indicator">
            <i class="material-icons">expand_more</i>
            <span>Pull to refresh</span>
        </div>
    `;
    
    const mainContent = document.querySelector('.main-content');
    if (mainContent) {
        mainContent.insertBefore(pullToRefreshElement, mainContent.firstChild);
    }
    
    document.addEventListener('touchstart', (e) => {
        if (window.scrollY === 0 && !isRefreshing) {
            startY = e.touches[0].clientY;
        }
    }, { passive: true });
    
    document.addEventListener('touchmove', (e) => {
        if (window.scrollY === 0 && !isRefreshing && startY > 0) {
            pullDistance = Math.min(e.touches[0].clientY - startY, maxPullDistance);
            
            if (pullDistance > 0) {
                e.preventDefault();
                updatePullIndicator(pullDistance);
            }
        }
    });
    
    document.addEventListener('touchend', () => {
        if (pullDistance > refreshThreshold && !isRefreshing) {
            triggerRefresh();
        } else {
            resetPullIndicator();
        }
        
        startY = 0;
        pullDistance = 0;
    });
    
    function updatePullIndicator(distance) {
        pullToRefreshElement.style.transform = `translateY(${distance}px)`;
        
        const indicator = pullToRefreshElement.querySelector('.pull-indicator');
        const icon = indicator.querySelector('i');
        const text = indicator.querySelector('span');
        
        if (distance > refreshThreshold) {
            icon.textContent = 'refresh';
            text.textContent = 'Release to refresh';
            pullToRefreshElement.classList.add('ready');
        } else {
            icon.textContent = 'expand_more';
            text.textContent = 'Pull to refresh';
            pullToRefreshElement.classList.remove('ready');
        }
    }
    
    function triggerRefresh() {
        isRefreshing = true;
        pullToRefreshElement.classList.add('refreshing');
        
        const indicator = pullToRefreshElement.querySelector('.pull-indicator');
        indicator.innerHTML = '<i class="material-icons spin">refresh</i><span>Refreshing...</span>';
        
        // Perform refresh
        setTimeout(() => {
            window.location.reload();
        }, 1000);
    }
    
    function resetPullIndicator() {
        pullToRefreshElement.style.transform = 'translateY(0)';
        pullToRefreshElement.classList.remove('ready', 'refreshing');
        
        const indicator = pullToRefreshElement.querySelector('.pull-indicator');
        indicator.innerHTML = '<i class="material-icons">expand_more</i><span>Pull to refresh</span>';
    }
}

// Responsive Charts Setup
function setupResponsiveCharts() {
    // Make Chart.js responsive
    if (window.Chart) {
        Chart.defaults.responsive = true;
        Chart.defaults.maintainAspectRatio = false;
    }
    
    // Handle chart container resizing
    const chartContainers = document.querySelectorAll('.chart-container');
    chartContainers.forEach(container => {
        const observer = new ResizeObserver(entries => {
            for (let entry of entries) {
                const chart = Chart.getChart(entry.target.querySelector('canvas'));
                if (chart) {
                    chart.resize();
                }
            }
        });
        
        observer.observe(container);
    });
}

// Virtual Keyboard Handling
function setupVirtualKeyboard() {
    let initialViewportHeight = window.innerHeight;
    
    window.addEventListener('resize', () => {
        const currentHeight = window.innerHeight;
        const heightDifference = initialViewportHeight - currentHeight;
        
        // Detect virtual keyboard
        if (heightDifference > 150) {
            document.body.classList.add('keyboard-open');
            
            // Scroll active input into view
            const activeElement = document.activeElement;
            if (activeElement && (activeElement.tagName === 'INPUT' || activeElement.tagName === 'TEXTAREA')) {
                setTimeout(() => {
                    activeElement.scrollIntoView({ behavior: 'smooth', block: 'center' });
                }, 300);
            }
        } else {
            document.body.classList.remove('keyboard-open');
        }
    });
}

// Touch Optimizations
function setupTouchOptimizations() {
    // Improve touch target sizes
    const touchTargets = document.querySelectorAll('button, a, input, select, textarea');
    touchTargets.forEach(target => {
        const rect = target.getBoundingClientRect();
        if (rect.height < 44) {
            target.style.minHeight = '44px';
            target.style.display = 'inline-flex';
            target.style.alignItems = 'center';
        }
    });
    
    // Add touch feedback
    document.addEventListener('touchstart', (e) => {
        if (e.target.matches('button, .btn, a')) {
            e.target.classList.add('touch-active');
        }
    });
    
    document.addEventListener('touchend', (e) => {
        if (e.target.matches('button, .btn, a')) {
            setTimeout(() => {
                e.target.classList.remove('touch-active');
            }, 150);
        }
    });
}

// Quick action functions
function quickAddActivity() {
    toggleFabMenu();
    window.location.href = '/activities/create/';
}

function quickAddInventory() {
    toggleFabMenu();
    window.location.href = '/inventory/items/create/';
}

function quickViewCalendar() {
    toggleFabMenu();
    window.location.href = '/farms/crop_calendar/';
}

// Utility functions
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

function autoSaveForm(e) {
    const form = e.target.form;
    if (!form) return;
    
    const formData = new FormData(form);
    const data = {};
    
    for (let [key, value] of formData.entries()) {
        data[key] = value;
    }
    
    localStorage.setItem(`form_${form.id || 'default'}`, JSON.stringify(data));
    showNotification('Form auto-saved', 'info');
}

function toggleZoom(element) {
    element.classList.toggle('zoomed');
    
    if (element.classList.contains('zoomed')) {
        element.style.transform = 'scale(1.5)';
        element.style.zIndex = '1000';
        element.style.position = 'relative';
    } else {
        element.style.transform = '';
        element.style.zIndex = '';
        element.style.position = '';
    }
}

function handleRightEdgeSwipe() {
    // Could implement back navigation or other features
    if (window.history.length > 1) {
        window.history.back();
    }
}

function showSearchModal() {
    // Implement search modal
    console.log('Show search modal');
}

function showNotifications() {
    // Implement notifications panel
    console.log('Show notifications');
}

// Export functions for global use
window.mobileOptimizations = {
    setupMobileNavigation,
    setupTouchGestures,
    setupMobileTables,
    setupMobileForms,
    setupQuickActions,
    setupPullToRefresh,
    toggleFabMenu,
    quickAddActivity,
    quickAddInventory,
    quickViewCalendar
};