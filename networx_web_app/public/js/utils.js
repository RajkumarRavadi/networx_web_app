// Utility functions for NETWORX web app

// Check if user is authenticated
const checkAuth = () => {
	return frappe.session.user && frappe.session.user !== 'Guest';
};

// Redirect to login if not authenticated
const requireAuth = () => {
	if (!checkAuth()) {
		window.location.href = '/login';
		return false;
	}
	return true;
};

// Format date to readable string
const formatDate = (dateString) => {
	if (!dateString) return 'N/A';
	const date = new Date(dateString);
	return date.toLocaleDateString('en-US', {
		year: 'numeric',
		month: 'short',
		day: 'numeric'
	});
};

// Format datetime to readable string
const formatDateTime = (dateString) => {
	if (!dateString) return 'N/A';
	const date = new Date(dateString);
	return date.toLocaleString('en-US', {
		year: 'numeric',
		month: 'short',
		day: 'numeric',
		hour: '2-digit',
		minute: '2-digit'
	});
};

let toastContainer = null;

const ensureToastContainer = () => {
	if (toastContainer) return toastContainer;

	toastContainer = document.createElement('div');
	toastContainer.style.position = 'fixed';
	toastContainer.style.top = '1.5rem';
	toastContainer.style.right = '1.5rem';
	toastContainer.style.zIndex = '9999';
	toastContainer.style.display = 'flex';
	toastContainer.style.flexDirection = 'column';
	toastContainer.style.gap = '0.75rem';
	document.body.appendChild(toastContainer);

	return toastContainer;
};

const fallbackToast = (message, type) => {
	const container = ensureToastContainer();
	const toast = document.createElement('div');
	const palette = {
		success: '#34d399',
		error: '#f87171',
		warning: '#fbbf24',
		info: '#60a5fa'
	};

	toast.textContent = message;
	toast.style.padding = '0.85rem 1rem';
	toast.style.borderRadius = '999px';
	toast.style.fontSize = '0.9rem';
	toast.style.fontWeight = '600';
	toast.style.color = '#0f172a';
	toast.style.backgroundColor = palette[type] || palette.success;
	toast.style.boxShadow = '0 10px 25px rgba(15, 23, 42, 0.12)';
	toast.style.opacity = '0';
	toast.style.transform = 'translateY(-10px)';
	toast.style.transition = 'opacity 150ms ease, transform 150ms ease';

	container.appendChild(toast);

	requestAnimationFrame(() => {
		toast.style.opacity = '1';
		toast.style.transform = 'translateY(0)';
	});

	setTimeout(() => {
		toast.style.opacity = '0';
		toast.style.transform = 'translateY(-10px)';
		setTimeout(() => toast.remove(), 180);
	}, 2500);
};

// Show toast notification
const showToast = (message, type = 'success') => {
	if (window.frappe && typeof frappe.show_alert === 'function') {
		frappe.show_alert(
			{
				message,
				indicator: type
			},
			5
		);
		return;
	}

	fallbackToast(message, type);
};

// Show loading indicator
const showLoading = () => {
	if (window.frappe && typeof frappe.freeze === 'function') {
		frappe.freeze();
	}
};

// Hide loading indicator
const hideLoading = () => {
	if (window.frappe && typeof frappe.unfreeze === 'function') {
		frappe.unfreeze();
	}
};

// Get query parameter from URL
const getQueryParam = (param) => {
	const urlParams = new URLSearchParams(window.location.search);
	return urlParams.get(param);
};

// Set page title
const setPageTitle = (title) => {
	document.title = `${title} - NETWORX`;
};

// Export utilities
window.NetworkxUtils = {
	checkAuth,
	requireAuth,
	formatDate,
	formatDateTime,
	showToast,
	showLoading,
	hideLoading,
	getQueryParam,
	setPageTitle
};



