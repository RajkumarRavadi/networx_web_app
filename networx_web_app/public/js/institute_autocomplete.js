// Institute Autocomplete Component for NETWORX Web App

class InstituteAutocomplete {
	constructor(inputElement, hiddenInputElement = null, options = {}) {
		this.inputElement = inputElement;
		this.hiddenInputElement = hiddenInputElement; // For storing institute Link value
		this.options = {
			minChars: 2,
			delay: 300,
			limit: 20,
			...options
		};

		this.dropdown = null;
		this.searchTimeout = null;
		this.selectedInstitute = null;
		this.isOpen = false;
		this.selectedIndex = -1;

		this.init();
	}

	init() {
		// Create dropdown container
		this.createDropdown();

		// Attach event listeners
		this.inputElement.addEventListener('input', (e) => this.handleInput(e));
		this.inputElement.addEventListener('keydown', (e) => this.handleKeyDown(e));
		this.inputElement.addEventListener('focus', () => this.handleFocus());
		this.inputElement.addEventListener('blur', () => {
			// Delay to allow click events on dropdown
			setTimeout(() => this.handleBlur(), 200);
		});

		// Close dropdown when clicking outside
		document.addEventListener('click', (e) => {
			if (!this.inputElement.contains(e.target) &&
				!this.dropdown.contains(e.target)) {
				this.closeDropdown();
			}
		});
	}

	createDropdown() {
		this.dropdown = document.createElement('div');
		this.dropdown.className = 'institute-autocomplete-dropdown';

		// Get theme-aware background color
		const isDark = document.documentElement.getAttribute('data-theme') === 'dark';
		const bgColor = isDark ? '#1a1a1a' : '#ffffff';
		const textColor = isDark ? '#ffffff' : '#1a1a1a';
		const borderColor = isDark ? 'rgba(255,255,255,0.1)' : 'rgba(0,0,0,0.1)';

		this.dropdown.style.cssText = `
			position: absolute;
			top: 100%;
			left: 0;
			right: 0;
			z-index: 9999;
			background: ${bgColor};
			border: 1px solid ${borderColor};
			border-radius: 8px;
			margin-top: 4px;
			max-height: 300px;
			overflow-y: auto;
			box-shadow: 0 4px 12px rgba(0,0,0,0.3);
			display: none;
			backdrop-filter: blur(10px);
			-webkit-backdrop-filter: blur(10px);
		`;

		// Insert dropdown after input element
		this.inputElement.parentElement.style.position = 'relative';
		this.inputElement.parentElement.appendChild(this.dropdown);
	}

	async handleInput(e) {
		const query = e.target.value.trim();

		// Clear selection if input is cleared
		if (!query) {
			this.selectedInstitute = null;
			if (this.hiddenInputElement) {
				this.hiddenInputElement.value = '';
			}
			this.closeDropdown();
			return;
		}

		// Clear previous timeout
		if (this.searchTimeout) {
			clearTimeout(this.searchTimeout);
		}

		// Debounce search
		this.searchTimeout = setTimeout(() => {
			this.searchInstitutes(query);
		}, this.options.delay);
	}

	async searchInstitutes(query) {
		if (query.length < this.options.minChars) {
			this.closeDropdown();
			return;
		}

		// Show loading state
		this.showLoading();

		try {
			if (!window.frappe || !window.frappe.call) {
				throw new Error('Frappe is not initialized');
			}

			const response = await window.frappe.call({
				method: 'networx_web_app.networx_web_app.api.search_institutes',
				args: {
					query: query,
					limit: this.options.limit
				}
			});

			if (response && response.message) {
				const data = response.message;
				if (data.success && data.institutes) {
					this.renderDropdown(data.institutes);
				} else {
					this.showNoResults();
				}
			} else {
				this.showNoResults();
			}
		} catch (error) {
			console.error('Error searching institutes:', error);
			this.showError('Failed to search institutes. Please try again.');
		}
	}

	renderDropdown(institutes) {
		if (!institutes || institutes.length === 0) {
			this.showNoResults();
			return;
		}

		const isDark = document.documentElement.getAttribute('data-theme') === 'dark';
		const bgColor = isDark ? '#1a1a1a' : '#ffffff';
		const textColor = isDark ? '#ffffff' : '#1a1a1a';
		const borderColor = isDark ? 'rgba(255,255,255,0.05)' : 'rgba(0,0,0,0.05)';
		const hoverBg = isDark ? 'rgba(255,255,255,0.1)' : 'rgba(0,0,0,0.05)';
		const textMuted = isDark ? 'rgba(255,255,255,0.6)' : 'rgba(0,0,0,0.6)';
		const primaryColor = isDark ? '#a855f7' : '#7c3aed';

		this.dropdown.style.background = bgColor;
		this.dropdown.innerHTML = '';
		this.selectedIndex = -1;

		institutes.forEach((institute, index) => {
			const item = document.createElement('div');
			item.className = 'institute-autocomplete-item';
			item.dataset.index = index;
			item.dataset.instituteId = institute.name;
			item.style.cssText = `
				padding: 12px 16px;
				cursor: pointer;
				border-bottom: 1px solid ${borderColor};
				transition: background-color 0.2s;
			`;
			item.style.color = textColor;

			// Institute name (bold)
			const nameDiv = document.createElement('div');
			nameDiv.style.fontWeight = '600';
			nameDiv.style.marginBottom = '4px';
			nameDiv.textContent = institute.institute_name;

			// Institute details (smaller, muted)
			const detailsDiv = document.createElement('div');
			detailsDiv.style.cssText = `
				font-size: 0.875rem;
				color: ${textMuted};
			`;
			const details = [];
			if (institute.institute_type) details.push(institute.institute_type);
			if (institute.city) details.push(institute.city);
			if (institute.state) details.push(institute.state);
			detailsDiv.textContent = details.join(' • ') || '';

			item.appendChild(nameDiv);
			item.appendChild(detailsDiv);

			// Hover effect
			item.addEventListener('mouseenter', () => {
				item.style.backgroundColor = hoverBg;
				this.selectedIndex = index;
			});

			item.addEventListener('mouseleave', () => {
				item.style.backgroundColor = 'transparent';
			});

			// Click to select
			item.addEventListener('click', () => {
				this.selectInstitute(institute);
			});

			this.dropdown.appendChild(item);
		});

		// Add manual entry option at the bottom
		const manualEntryDiv = document.createElement('div');
		manualEntryDiv.className = 'manual-entry-option';
		manualEntryDiv.style.cssText = `
			padding: 12px 16px;
			cursor: pointer;
			transition: background-color 0.2s;
			border-top: 1px solid ${isDark ? 'rgba(255,255,255,0.1)' : 'rgba(0,0,0,0.1)'};
			color: ${primaryColor};
			font-weight: 500;
			display: flex;
			align-items: center;
			gap: 8px;
		`;
		manualEntryDiv.innerHTML = `
			<i class="ri-edit-line"></i>
			<span>Not found? Use manual entry: "${this.inputElement.value.trim()}"</span>
		`;

		manualEntryDiv.addEventListener('mouseenter', () => {
			manualEntryDiv.style.backgroundColor = hoverBg;
		});
		manualEntryDiv.addEventListener('mouseleave', () => {
			manualEntryDiv.style.backgroundColor = 'transparent';
		});
		manualEntryDiv.addEventListener('click', () => {
			this.useManualEntry();
		});

		this.dropdown.appendChild(manualEntryDiv);
		this.openDropdown();
	}

	selectInstitute(institute) {
		this.selectedInstitute = institute;
		this.inputElement.value = institute.institute_name;

		// Store institute Link value in hidden input if provided
		if (this.hiddenInputElement) {
			this.hiddenInputElement.value = institute.name;
		}

		// Store in data attribute as well
		this.inputElement.dataset.instituteId = institute.name;

		this.closeDropdown();

		// Trigger custom event
		const event = new CustomEvent('instituteSelected', {
			detail: { institute: institute }
		});
		this.inputElement.dispatchEvent(event);
	}

	handleKeyDown(e) {
		if (!this.isOpen) {
			if (e.key === 'ArrowDown' || e.key === 'Enter') {
				const query = this.inputElement.value.trim();
				if (query.length >= this.options.minChars) {
					this.searchInstitutes(query);
				}
			}
			return;
		}

		const items = this.dropdown.querySelectorAll('.institute-autocomplete-item');

		switch (e.key) {
			case 'ArrowDown':
				e.preventDefault();
				this.selectedIndex = Math.min(this.selectedIndex + 1, items.length - 1);
				this.highlightItem(items);
				break;

			case 'ArrowUp':
				e.preventDefault();
				this.selectedIndex = Math.max(this.selectedIndex - 1, -1);
				this.highlightItem(items);
				break;

			case 'Enter':
				e.preventDefault();
				if (this.selectedIndex >= 0 && items[this.selectedIndex]) {
					const instituteId = items[this.selectedIndex].dataset.instituteId;
					const institute = this.getInstituteFromItem(items[this.selectedIndex]);
					if (institute) {
						this.selectInstitute(institute);
					}
				}
				break;

			case 'Escape':
				e.preventDefault();
				this.closeDropdown();
				break;
		}
	}

	highlightItem(items) {
		const isDark = document.documentElement.getAttribute('data-theme') === 'dark';
		const hoverBg = isDark ? 'rgba(255,255,255,0.1)' : 'rgba(0,0,0,0.05)';

		items.forEach((item, index) => {
			if (index === this.selectedIndex) {
				item.style.backgroundColor = hoverBg;
				item.scrollIntoView({ block: 'nearest', behavior: 'smooth' });
			} else {
				item.style.backgroundColor = 'transparent';
			}
		});
	}

	getInstituteFromItem(item) {
		// Extract institute data from item
		const nameDiv = item.querySelector('div:first-child');
		const instituteName = nameDiv ? nameDiv.textContent : '';
		const instituteId = item.dataset.instituteId;

		return {
			name: instituteId,
			institute_name: instituteName
		};
	}

	handleFocus() {
		const query = this.inputElement.value.trim();
		if (query.length >= this.options.minChars && !this.isOpen) {
			this.searchInstitutes(query);
		}
	}

	handleBlur() {
		// Don't close if clicking on dropdown
		if (this.dropdown && this.dropdown.contains(document.activeElement)) {
			return;
		}
		// Close dropdown after a short delay to allow click events
	}

	openDropdown() {
		this.dropdown.style.display = 'block';
		this.isOpen = true;
	}

	closeDropdown() {
		this.dropdown.style.display = 'none';
		this.isOpen = false;
		this.selectedIndex = -1;
	}

	showLoading() {
		const isDark = document.documentElement.getAttribute('data-theme') === 'dark';
		const textMuted = isDark ? 'rgba(255,255,255,0.6)' : 'rgba(0,0,0,0.6)';
		const bgColor = isDark ? '#1a1a1a' : '#ffffff';

		this.dropdown.style.background = bgColor;
		this.dropdown.innerHTML = `
			<div style="padding: 16px; text-align: center; color: ${textMuted};">
				<i class="ri-loader-4-line animate-spin" style="display: inline-block;"></i>
				<span style="margin-left: 8px;">Searching...</span>
			</div>
		`;
		this.openDropdown();
	}

	showNoResults() {
		const isDark = document.documentElement.getAttribute('data-theme') === 'dark';
		const textMuted = isDark ? 'rgba(255,255,255,0.6)' : 'rgba(0,0,0,0.6)';
		const primaryColor = isDark ? '#a855f7' : '#7c3aed';
		const hoverBg = isDark ? 'rgba(255,255,255,0.1)' : 'rgba(0,0,0,0.05)';

		this.dropdown.innerHTML = `
			<div style="padding: 12px 16px; text-align: center; color: ${textMuted}; border-bottom: 1px solid ${isDark ? 'rgba(255,255,255,0.05)' : 'rgba(0,0,0,0.05)'};">
				No institutes found. Try a different search term.
			</div>
			<div class="manual-entry-option" style="
				padding: 12px 16px;
				cursor: pointer;
				transition: background-color 0.2s;
				border-top: 1px solid ${isDark ? 'rgba(255,255,255,0.1)' : 'rgba(0,0,0,0.1)'};
				color: ${primaryColor};
				font-weight: 500;
				display: flex;
				align-items: center;
				gap: 8px;
			">
				<i class="ri-edit-line"></i>
				<span>Use manual entry: "${this.inputElement.value.trim()}"</span>
			</div>
		`;

		// Add click handler for manual entry
		const manualOption = this.dropdown.querySelector('.manual-entry-option');
		if (manualOption) {
			manualOption.addEventListener('mouseenter', () => {
				manualOption.style.backgroundColor = hoverBg;
			});
			manualOption.addEventListener('mouseleave', () => {
				manualOption.style.backgroundColor = 'transparent';
			});
			manualOption.addEventListener('click', () => {
				this.useManualEntry();
			});
		}

		this.openDropdown();
	}

	useManualEntry() {
		// Clear the institute Link (user is entering manually)
		if (this.hiddenInputElement) {
			this.hiddenInputElement.value = '';
		}
		this.inputElement.dataset.instituteId = '';
		this.selectedInstitute = null;

		// Keep the current input value (user's manual entry)
		// Just close the dropdown
		this.closeDropdown();

		// Trigger custom event for manual entry
		const event = new CustomEvent('instituteManualEntry', {
			detail: { value: this.inputElement.value.trim() }
		});
		this.inputElement.dispatchEvent(event);
	}

	showError(message) {
		const isDark = document.documentElement.getAttribute('data-theme') === 'dark';
		const bgColor = isDark ? '#1a1a1a' : '#ffffff';

		this.dropdown.style.background = bgColor;
		this.dropdown.innerHTML = `
			<div style="padding: 16px; text-align: center; color: #ef4444;">
				${message}
			</div>
			<div class="manual-entry-option" style="
				padding: 12px 16px;
				cursor: pointer;
				transition: background-color 0.2s;
				border-top: 1px solid ${isDark ? 'rgba(255,255,255,0.1)' : 'rgba(0,0,0,0.1)'};
				color: ${isDark ? '#a855f7' : '#7c3aed'};
				font-weight: 500;
				display: flex;
				align-items: center;
				gap: 8px;
			">
				<i class="ri-edit-line"></i>
				<span>Use manual entry instead</span>
			</div>
		`;

		// Add click handler for manual entry
		const manualOption = this.dropdown.querySelector('.manual-entry-option');
		if (manualOption) {
			manualOption.addEventListener('mouseenter', () => {
				manualOption.style.backgroundColor = isDark ? 'rgba(255,255,255,0.1)' : 'rgba(0,0,0,0.05)';
			});
			manualOption.addEventListener('mouseleave', () => {
				manualOption.style.backgroundColor = 'transparent';
			});
			manualOption.addEventListener('click', () => {
				this.useManualEntry();
			});
		}

		this.openDropdown();
	}

	// Public method to get selected institute
	getSelectedInstitute() {
		return this.selectedInstitute;
	}

	// Public method to clear selection
	clear() {
		this.inputElement.value = '';
		if (this.hiddenInputElement) {
			this.hiddenInputElement.value = '';
		}
		this.selectedInstitute = null;
		this.inputElement.dataset.instituteId = '';
		this.closeDropdown();
	}
}

// Export to global scope
window.InstituteAutocomplete = InstituteAutocomplete;
