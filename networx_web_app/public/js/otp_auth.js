// OTP Authentication Manager for NETWORX Web App

class OTPAuthManager {
    constructor() {
        this.resendCountdown = 0;
        this.countdownInterval = null;
    }

    validateEmail(email) {
        if (!email) return false;
        const pattern = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
        return pattern.test(email);
    }

    validateOTP(otp) {
        if (!otp) return false;
        return /^\d{6}$/.test(otp);
    }

    async handleSendOTP(email) {
        if (!this.validateEmail(email)) {
            return {
                success: false,
                message: "Please enter a valid email address"
            };
        }

        try {
            if (!window.frappe || !window.frappe.call) {
                throw new Error('Frappe is not initialized');
            }

            const response = await window.frappe.call({
                method: 'networx_web_app.networx_web_app.api.generate_and_send_otp',
                type: 'POST',
                args: {
                    email: email
                },
                freeze: true,
                freeze_message: 'Sending OTP...'
            });

            if (response && response.message) {
                return response.message;
            }
            return response;
        } catch (error) {
            console.error('Error sending OTP:', error);
            return {
                success: false,
                message: error.message || 'Failed to send OTP. Please try again.'
            };
        }
    }

    async handleVerifyOTP(email, otpCode) {
        if (!this.validateEmail(email)) {
            return {
                success: false,
                message: "Please enter a valid email address"
            };
        }

        if (!this.validateOTP(otpCode)) {
            return {
                success: false,
                message: "Please enter a valid 6-digit OTP code"
            };
        }

        try {
            if (!window.frappe || !window.frappe.call) {
                throw new Error('Frappe is not initialized');
            }

            const response = await window.frappe.call({
                method: 'networx_web_app.networx_web_app.api.verify_otp_and_login',
                type: 'POST',
                args: {
                    email: email,
                    otp_code: otpCode
                },
                freeze: true,
                freeze_message: 'Verifying OTP...'
            });

            if (response && response.message) {
                return response.message;
            }
            return response;
        } catch (error) {
            console.error('Error verifying OTP:', error);
            return {
                success: false,
                message: error.message || 'Failed to verify OTP. Please try again.'
            };
        }
    }

    async handleResendOTP(email) {
        if (!this.validateEmail(email)) {
            return {
                success: false,
                message: "Please enter a valid email address"
            };
        }

        try {
            if (!window.frappe || !window.frappe.call) {
                throw new Error('Frappe is not initialized');
            }

            const response = await window.frappe.call({
                method: 'networx_web_app.networx_web_app.api.resend_otp',
                type: 'POST',
                args: {
                    email: email
                },
                freeze: true,
                freeze_message: 'Resending OTP...'
            });

            if (response && response.message) {
                return response.message;
            }
            return response;
        } catch (error) {
            console.error('Error resending OTP:', error);
            return {
                success: false,
                message: error.message || 'Failed to resend OTP. Please try again.'
            };
        }
    }

    startResendCountdown(seconds = 60, callback) {
        this.resendCountdown = seconds;
        this.clearCountdown();

        this.countdownInterval = setInterval(() => {
            this.resendCountdown--;
            if (callback) {
                callback(this.resendCountdown);
            }

            if (this.resendCountdown <= 0) {
                this.clearCountdown();
            }
        }, 1000);
    }

    clearCountdown() {
        if (this.countdownInterval) {
            clearInterval(this.countdownInterval);
            this.countdownInterval = null;
        }
    }

    autoSubmitOTP(otpInput, email, verifyCallback) {
        otpInput.addEventListener('input', (e) => {
            const value = e.target.value.replace(/\D/g, ''); // Remove non-digits
            e.target.value = value.slice(0, 6); // Limit to 6 digits

            // Auto-submit when 6 digits are entered
            if (value.length === 6) {
                if (verifyCallback) {
                    verifyCallback(email, value);
                }
            }
        });

        // Prevent non-numeric input
        otpInput.addEventListener('keypress', (e) => {
            if (!/[0-9]/.test(e.key) && !['Backspace', 'Delete', 'Tab', 'ArrowLeft', 'ArrowRight'].includes(e.key)) {
                e.preventDefault();
            }
        });
    }
}

// Export to global scope
window.OTPAuthManager = OTPAuthManager;
