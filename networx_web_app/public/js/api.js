// API wrapper functions for NETWORX web app

const NetworkxAPI = {
	// Get dashboard statistics
	getDashboardStats: async () => {
		try {
			const response = await frappe.call({
				method: 'networx_web_app.networx_web_app.api.get_dashboard_stats',
				freeze: true
			});
			return response.message;
		} catch (error) {
			console.error('Error fetching dashboard stats:', error);
			throw error;
		}
	},

	// Get job listings
	getJobListings: async (filters = {}, limit = 20, offset = 0, searchTerm = null) => {
		try {
			const response = await frappe.call({
				method: 'networx_web_app.networx_web_app.api.get_job_listings',
				args: {
					filters: filters,
					limit: limit,
					offset: offset,
					search_term: searchTerm
				}
			});
			return response.message;
		} catch (error) {
			console.error('Error fetching job listings:', error);
			throw error;
		}
	},

	// Get job detail
	getJobDetail: async (jobId) => {
		try {
			const response = await frappe.call({
				method: 'networx_web_app.networx_web_app.api.get_job_detail',
				args: {
					job_id: jobId
				},
				freeze: true
			});
			return response.message;
		} catch (error) {
			console.error('Error fetching job detail:', error);
			throw error;
		}
	},

	// Apply for job
	applyForJob: async (jobId, coverLetter) => {
		try {
			const response = await frappe.call({
				method: 'networx_web_app.networx_web_app.api.apply_for_job',
				args: {
					job_id: jobId,
					cover_letter: coverLetter
				},
				freeze: true,
				freeze_message: 'Submitting application...'
			});
			return response.message;
		} catch (error) {
			console.error('Error applying for job:', error);
			throw error;
		}
	},

	// Get student profile
	getStudentProfile: async (user = null) => {
		try {
			const response = await frappe.call({
				method: 'networx_web_app.networx_web_app.api.get_student_profile',
				args: {
					user: user
				}
			});
			return response.message;
		} catch (error) {
			console.error('Error fetching student profile:', error);
			throw error;
		}
	},

	// Update student profile
	updateStudentProfile: async (data) => {
		try {
			const response = await frappe.call({
				method: 'networx_web_app.networx_web_app.api.update_student_profile',
				args: {
					data: data
				},
				freeze: true,
				freeze_message: 'Updating profile...'
			});
			return response.message;
		} catch (error) {
			console.error('Error updating profile:', error);
			throw error;
		}
	},

	// Get recent events
	getRecentEvents: async (limit = 5) => {
		try {
			const response = await frappe.call({
				method: 'networx_web_app.networx_web_app.api.get_recent_events',
				args: {
					limit: limit
				}
			});
			return response.message;
		} catch (error) {
			console.error('Error fetching events:', error);
			throw error;
		}
	},

	// Get student profile by ID or email
	getStudentProfileByIdOrEmail: async (profileId = null, email = null) => {
		try {
			const response = await frappe.call({
				method: 'networx_web_app.networx_web_app.api.get_student_profile_by_id_or_email',
				args: {
					profile_id: profileId,
					email: email
				}
			});
			return response.message;
		} catch (error) {
			console.error('Error fetching student profile:', error);
			throw error;
		}
	},

	// Get user profile details
	getUserProfileDetails: async (user = null) => {
		try {
			console.log('Calling getUserProfileDetails...');

			// Build args object - only include user if it's provided
			const args = {};
			if (user) {
				args.user = user;
			}

			console.log('API args:', args);

			const response = await frappe.call({
				method: 'networx_web_app.networx_web_app.apis.user_profile.user_profile_details.get_user_profile_details',
				args: Object.keys(args).length > 0 ? args : undefined
			});

			console.log('API response:', response);

			if (response && response.message) {
				return response.message;
			} else if (response) {
				return response;
			} else {
				throw new Error('Invalid response from server');
			}
		} catch (error) {
			console.error('Error fetching user profile details:', error);
			console.error('Error details:', {
				message: error.message,
				response: error.response,
				error: error
			});

			// Extract error message from Frappe error response
			let errorMessage = error.message || 'Unknown error occurred';

			if (error.message) {
				if (error.message.includes('User Profile not found')) {
					errorMessage = 'Profile not found. Please create your profile first.';
				} else if (error.message.includes('Please login')) {
					errorMessage = 'Please login to view your profile.';
				} else if (error.response && error.response.exc) {
					errorMessage = error.response.exc;
				} else if (error.response && error.response.message) {
					errorMessage = error.response.message;
				}
			}

			const newError = new Error(errorMessage);
			newError.response = error.response;
			throw newError;
		}
	},

	// Update user profile (User Profile doctype)
	updateUserProfile: async (data) => {
		try {
			const response = await frappe.call({
				method: 'networx_web_app.networx_web_app.apis.user_profile.update_user_profile.update_user_profile',
				args: {
					data: data
				},
				freeze: true,
				freeze_message: 'Updating profile...'
			});
			return response.message;
		} catch (error) {
			console.error('Error updating user profile:', error);
			throw error;
		}
	},

	// Get recent applications
	getRecentApplications: async (limit = 5) => {
		try {
			const response = await frappe.call({
				method: 'networx_web_app.networx_web_app.api.get_recent_applications',
				args: {
					limit: limit
				}
			});
			return response.message;
		} catch (error) {
			console.error('Error fetching applications:', error);
			throw error;
		}
	}
};

// Export API object
window.NetworkxAPI = NetworkxAPI;



