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

// Show toast notification
const showToast = (message, type = 'success') => {
	frappe.show_alert({
		message: message,
		indicator: type
	}, 5);
};

// Show loading indicator
const showLoading = () => {
	frappe.freeze();
};

// Hide loading indicator
const hideLoading = () => {
	frappe.unfreeze();
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



