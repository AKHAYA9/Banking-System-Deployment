// ==========================================
// DASHBOARD JAVASCRIPT - SecureBank
// Complete functionality for responsive dashboard
// ==========================================

document.addEventListener('DOMContentLoaded', function() {
    initializeDashboard();
});

// ==========================================
// INITIALIZE DASHBOARD
// ==========================================
function initializeDashboard() {
    setupSidebar();
    setupMessages();
    setupTables();
    setupAnimations();
}

// ==========================================
// SIDEBAR FUNCTIONALITY
// ==========================================
function setupSidebar() {
    const menuToggle = document.getElementById('menuToggle');
    const closeSidebar = document.getElementById('closeSidebar');
    const sidebar = document.getElementById('sidebar');
    const sidebarOverlay = document.getElementById('sidebarOverlay');

    // Open sidebar on mobile
    if (menuToggle) {
        menuToggle.addEventListener('click', function() {
            sidebar.classList.add('active');
            sidebarOverlay.classList.add('active');
            document.body.style.overflow = 'hidden';
        });
    }

    // Close sidebar
    if (closeSidebar) {
        closeSidebar.addEventListener('click', function() {
            closeSidebarPanel();
        });
    }

    // Close sidebar when clicking overlay
    if (sidebarOverlay) {
        sidebarOverlay.addEventListener('click', function() {
            closeSidebarPanel();
        });
    }

    // Close sidebar on ESC key
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape' && sidebar.classList.contains('active')) {
            closeSidebarPanel();
        }
    });

    // Handle window resize
    let resizeTimer;
    window.addEventListener('resize', function() {
        clearTimeout(resizeTimer);
        resizeTimer = setTimeout(function() {
            if (window.innerWidth > 768 && sidebar.classList.contains('active')) {
                closeSidebarPanel();
            }
        }, 250);
    });
}

function closeSidebarPanel() {
    const sidebar = document.getElementById('sidebar');
    const sidebarOverlay = document.getElementById('sidebarOverlay');
    
    sidebar.classList.remove('active');
    sidebarOverlay.classList.remove('active');
    document.body.style.overflow = '';
}

// ==========================================
// MESSAGES AUTO-DISMISS
// ==========================================
function setupMessages() {
    const messages = document.querySelectorAll('.alert, .message');
    
    messages.forEach(function(message) {
        // Auto dismiss after 5 seconds
        setTimeout(function() {
            fadeOutAndRemove(message);
        }, 5000);

        // Add close button functionality
        const closeBtn = message.querySelector('.close-btn, .btn-close');
        if (closeBtn) {
            closeBtn.addEventListener('click', function() {
                fadeOutAndRemove(message);
            });
        }
    });
}

function fadeOutAndRemove(element) {
    element.style.transition = 'opacity 0.5s, transform 0.5s';
    element.style.opacity = '0';
    element.style.transform = 'translateY(-20px)';
    
    setTimeout(function() {
        element.remove();
    }, 500);
}

// ==========================================
// TABLE ENHANCEMENTS
// ==========================================
function setupTables() {
    const tables = document.querySelectorAll('.data-table');
    
    tables.forEach(function(table) {
        // Add hover effect data
        const rows = table.querySelectorAll('tbody tr');
        rows.forEach(function(row) {
            row.addEventListener('click', function() {
                // Optional: Add row selection functionality
                this.classList.toggle('selected');
            });
        });

        // Make tables responsive
        makeTableResponsive(table);
    });
}

function makeTableResponsive(table) {
    // Wrap table in responsive container if not already wrapped
    if (!table.parentElement.classList.contains('table-responsive')) {
        const wrapper = document.createElement('div');
        wrapper.className = 'table-responsive';
        table.parentNode.insertBefore(wrapper, table);
        wrapper.appendChild(table);
    }
}

// ==========================================
// ANIMATIONS ON SCROLL
// ==========================================
function setupAnimations() {
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };

    const observer = new IntersectionObserver(function(entries) {
        entries.forEach(function(entry) {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
            }
        });
    }, observerOptions);

    // Animate cards on scroll
    const animatedElements = document.querySelectorAll(
        '.stat-card, .data-card, .form-card, .result-card, .action-btn'
    );

    animatedElements.forEach(function(element, index) {
        element.style.opacity = '0';
        element.style.transform = 'translateY(20px)';
        element.style.transition = `all 0.5s ease ${index * 0.1}s`;
        observer.observe(element);
    });
}

// ==========================================
// FORM UTILITIES
// ==========================================

// Confirm before delete
function confirmDelete(message) {
    return confirm(message || 'Are you sure you want to delete this item? This action cannot be undone.');
}

// Format currency input
function formatCurrency(input) {
    let value = input.value.replace(/[^\d.]/g, '');
    const parts = value.split('.');
    
    if (parts.length > 2) {
        value = parts[0] + '.' + parts.slice(1).join('');
    }
    
    if (parts[1] && parts[1].length > 2) {
        value = parts[0] + '.' + parts[1].substring(0, 2);
    }
    
    input.value = value;
}

// Validate phone number
function validatePhone(input) {
    const value = input.value.replace(/\D/g, '');
    if (value.length > 10) {
        input.value = value.substring(0, 10);
    } else {
        input.value = value;
    }
}

// Auto-format date input to today's date
function setTodayDate(inputId) {
    const input = document.getElementById(inputId);
    if (input && input.type === 'date') {
        const today = new Date().toISOString().split('T')[0];
        input.value = today;
        input.max = today;
    }
}

// ==========================================
// NOTIFICATION SYSTEM
// ==========================================
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.innerHTML = `
        <div class="notification-content">
            <i class="fas fa-${getNotificationIcon(type)}"></i>
            <span>${message}</span>
        </div>
        <button class="notification-close" onclick="this.parentElement.remove()">
            <i class="fas fa-times"></i>
        </button>
    `;
    
    // Add styles if not already in CSS
    notification.style.cssText = `
        position: fixed;
        top: 80px;
        right: 20px;
        padding: 15px 20px;
        background: white;
        border-radius: 8px;
        box-shadow: 0 5px 20px rgba(0,0,0,0.2);
        z-index: 9999;
        display: flex;
        align-items: center;
        gap: 15px;
        max-width: 400px;
        animation: slideInRight 0.3s ease;
    `;
    
    document.body.appendChild(notification);
    
    // Auto remove after 5 seconds
    setTimeout(function() {
        notification.style.animation = 'slideOutRight 0.3s ease';
        setTimeout(function() {
            notification.remove();
        }, 300);
    }, 5000);
}

function getNotificationIcon(type) {
    const icons = {
        success: 'check-circle',
        error: 'exclamation-circle',
        warning: 'exclamation-triangle',
        info: 'info-circle'
    };
    return icons[type] || 'info-circle';
}

// ==========================================
// LOADING SPINNER
// ==========================================
function showLoader() {
    const loader = document.createElement('div');
    loader.id = 'pageLoader';
    loader.innerHTML = `
        <div style="position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.5); display: flex; align-items: center; justify-content: center; z-index: 99999;">
            <div style="background: white; padding: 30px; border-radius: 12px; text-align: center;">
                <i class="fas fa-spinner fa-spin" style="font-size: 3rem; color: #0a3d62;"></i>
                <p style="margin-top: 15px; color: #0a3d62; font-weight: 600;">Loading...</p>
            </div>
        </div>
    `;
    document.body.appendChild(loader);
}

function hideLoader() {
    const loader = document.getElementById('pageLoader');
    if (loader) {
        loader.remove();
    }
}

// ==========================================
// STATISTICS COUNTER ANIMATION
// ==========================================
function animateValue(element, start, end, duration) {
    const range = end - start;
    const increment = range / (duration / 16);
    let current = start;
    
    const timer = setInterval(function() {
        current += increment;
        if ((increment > 0 && current >= end) || (increment < 0 && current <= end)) {
            current = end;
            clearInterval(timer);
        }
        element.textContent = Math.floor(current).toLocaleString();
    }, 16);
}

// Animate stat cards on page load
window.addEventListener('load', function() {
    const statNumbers = document.querySelectorAll('.stat-info h3');
    statNumbers.forEach(function(stat) {
        const value = parseInt(stat.textContent.replace(/[^\d]/g, ''));
        if (!isNaN(value) && value > 0) {
            stat.textContent = '0';
            setTimeout(function() {
                animateValue(stat, 0, value, 1000);
            }, 300);
        }
    });
});

// ==========================================
// SEARCH/FILTER FUNCTIONALITY
// ==========================================
function setupSearch(inputId, targetSelector) {
    const searchInput = document.getElementById(inputId);
    if (!searchInput) return;
    
    searchInput.addEventListener('input', function() {
        const searchTerm = this.value.toLowerCase();
        const items = document.querySelectorAll(targetSelector);
        
        items.forEach(function(item) {
            const text = item.textContent.toLowerCase();
            if (text.includes(searchTerm)) {
                item.style.display = '';
            } else {
                item.style.display = 'none';
            }
        });
    });
}

// ==========================================
// MODAL UTILITIES
// ==========================================
function openModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.style.display = 'flex';
        document.body.style.overflow = 'hidden';
    }
}

function closeModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.style.display = 'none';
        document.body.style.overflow = '';
    }
}

// Close modal on ESC key
document.addEventListener('keydown', function(e) {
    if (e.key === 'Escape') {
        const openModals = document.querySelectorAll('.modal-overlay[style*="display: flex"]');
        openModals.forEach(function(modal) {
            modal.style.display = 'none';
        });
        document.body.style.overflow = '';
    }
});

// ==========================================
// CLIPBOARD COPY
// ==========================================
function copyToClipboard(text, showMessage = true) {
    if (navigator.clipboard) {
        navigator.clipboard.writeText(text).then(function() {
            if (showMessage) {
                showNotification('Copied to clipboard!', 'success');
            }
        }).catch(function(err) {
            console.error('Failed to copy:', err);
        });
    } else {
        // Fallback for older browsers
        const textArea = document.createElement('textarea');
        textArea.value = text;
        textArea.style.position = 'fixed';
        textArea.style.opacity = '0';
        document.body.appendChild(textArea);
        textArea.select();
        document.execCommand('copy');
        document.body.removeChild(textArea);
        
        if (showMessage) {
            showNotification('Copied to clipboard!', 'success');
        }
    }
}

// ==========================================
// PRINT FUNCTIONALITY
// ==========================================
function printSection(sectionId) {
    const section = document.getElementById(sectionId);
    if (!section) return;
    
    const printWindow = window.open('', '', 'height=600,width=800');
    printWindow.document.write('<html><head><title>Print</title>');
    printWindow.document.write('<style>body { font-family: Arial, sans-serif; padding: 20px; }</style>');
    printWindow.document.write('</head><body>');
    printWindow.document.write(section.innerHTML);
    printWindow.document.write('</body></html>');
    printWindow.document.close();
    printWindow.print();
}

// ==========================================
// EXPORT TO CSV
// ==========================================
function exportTableToCSV(tableId, filename) {
    const table = document.getElementById(tableId);
    if (!table) return;
    
    let csv = [];
    const rows = table.querySelectorAll('tr');
    
    rows.forEach(function(row) {
        const cols = row.querySelectorAll('td, th');
        const rowData = [];
        
        cols.forEach(function(col) {
            rowData.push('"' + col.textContent.trim() + '"');
        });
        
        csv.push(rowData.join(','));
    });
    
    // Download CSV
    const csvContent = csv.join('\n');
    const blob = new Blob([csvContent], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename || 'export.csv';
    a.click();
    window.URL.revokeObjectURL(url);
}

// ==========================================
// FORM VALIDATION
// ==========================================
function validateForm(formId) {
    const form = document.getElementById(formId);
    if (!form) return true;
    
    const requiredFields = form.querySelectorAll('[required]');
    let isValid = true;
    
    requiredFields.forEach(function(field) {
        if (!field.value.trim()) {
            field.style.borderColor = '#dc3545';
            isValid = false;
            
            // Add error message
            let errorMsg = field.parentElement.querySelector('.error-message');
            if (!errorMsg) {
                errorMsg = document.createElement('small');
                errorMsg.className = 'error-message';
                errorMsg.style.color = '#dc3545';
                errorMsg.textContent = 'This field is required';
                field.parentElement.appendChild(errorMsg);
            }
        } else {
            field.style.borderColor = '';
            const errorMsg = field.parentElement.querySelector('.error-message');
            if (errorMsg) {
                errorMsg.remove();
            }
        }
    });
    
    return isValid;
}

// ==========================================
// UTILITY FUNCTIONS
// ==========================================

// Format number with commas
function formatNumber(num) {
    return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ',');
}

// Calculate percentage
function calculatePercentage(value, total) {
    if (total === 0) return 0;
    return ((value / total) * 100).toFixed(2);
}

// Debounce function for search
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

// ==========================================
// EXPORT FUNCTIONS FOR GLOBAL USE
// ==========================================
window.dashboardUtils = {
    showNotification,
    showLoader,
    hideLoader,
    copyToClipboard,
    printSection,
    exportTableToCSV,
    validateForm,
    openModal,
    closeModal,
    confirmDelete,
    formatCurrency,
    validatePhone,
    setTodayDate
};

// ==========================================
// CONSOLE LOG (Remove in production)
// ==========================================
console.log('✓ Dashboard JavaScript Loaded Successfully');
console.log('✓ All interactive features initialized');

