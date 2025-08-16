
        // Mobile Camera Permission Helper
        class MobileCameraHelper {
            constructor() {
                this.isIOS = /iPad|iPhone|iPod/.test(navigator.userAgent);
                this.isAndroid = /Android/.test(navigator.userAgent);
                this.isMobile = this.isIOS || this.isAndroid;
            }
            
            async requestCameraPermission() {
                // Check if permissions API is available
                if ('permissions' in navigator) {
                    try {
                        const permission = await navigator.permissions.query({ name: 'camera' });
                        console.log('Camera permission status:', permission.state);
                        
                        if (permission.state === 'denied') {
                            this.showPermissionDeniedHelp();
                            return false;
                        }
                    } catch (e) {
                        console.log('Permissions API not supported:', e);
                    }
                }
                
                return true;
            }
            
            showPermissionDeniedHelp() {
                const helpMessage = `
                    <div style="background: rgba(239, 68, 68, 0.1); padding: 20px; border-radius: 12px; border: 1px solid rgba(239, 68, 68, 0.3); margin: 20px 0;">
                        <h3 style="color: #ef4444; margin-bottom: 15px;">📱 Camera Permission Required</h3>
                        <p style="margin-bottom: 15px;">Camera access is blocked. Please enable it:</p>
                        
                        <div style="text-align: left; margin: 15px 0;">
                            <strong>For Chrome Mobile:</strong><br>
                            1. Tap the 🔒 or ⓘ icon in address bar<br>
                            2. Tap "Permissions" or "Site settings"<br>
                            3. Enable "Camera"<br>
                            4. Refresh this page<br><br>
                            
                            <strong>For Safari (iOS):</strong><br>
                            1. Go to Settings > Safari > Camera<br>
                            2. Select "Allow"<br>
                            3. Return to this page and refresh<br><br>
                            
                            <strong>For Brave Browser:</strong><br>
                            1. Tap the shield icon (🛡️) in address bar<br>
                            2. Enable "Camera" permission<br>
                            3. Refresh this page<br><br>
                            
                            <strong>Alternative:</strong><br>
                            • Try Chrome or Safari browsers<br>
                            • Use manual verification below
                        </div>
                        
                        <button onclick="location.reload()" style="background: #ef4444; color: white; border: none; padding: 12px 24px; border-radius: 8px; font-weight: 600; cursor: pointer;">
                            🔄 Refresh Page
                        </button>
                    </div>
                `;
                
                showResult(helpMessage, 'error');
            }
            
            async getCameraStream() {
                const constraints = {
                    video: {
                        facingMode: { ideal: 'environment' },
                        width: { min: 320, ideal: 640, max: 1920 },
                        height: { min: 240, ideal: 480, max: 1080 }
                    },
                    audio: false
                };
                
                // iOS Safari specific handling
                if (this.isIOS) {
                    // iOS requires user interaction before camera access
                    constraints.video.width = { ideal: 640 };
                    constraints.video.height = { ideal: 480 };
                }
                
                try {
                    // Try back camera first
                    return await navigator.mediaDevices.getUserMedia(constraints);
                } catch (backError) {
                    console.log('Back camera failed:', backError);
                    
                    // Try front camera
                    constraints.video.facingMode = { ideal: 'user' };
                    try {
                        return await navigator.mediaDevices.getUserMedia(constraints);
                    } catch (frontError) {
                        console.log('Front camera failed:', frontError);
                        
                        // Try any camera
                        return await navigator.mediaDevices.getUserMedia({ video: true });
                    }
                }
            }
            
            showCameraTroubleshooting(error) {
                let message = '';
                let solutions = '';
                
                switch (error.name) {
                    case 'NotAllowedError':
                        message = 'Camera permission was denied';
                        solutions = `
                            <strong>Solutions:</strong><br>
                            1. Check browser address bar for camera icon<br>
                            2. Click it and select "Allow"<br>
                            3. Refresh the page<br>
                            4. Try a different browser if needed
                        `;
                        break;
                        
                    case 'NotFoundError':
                        message = 'No camera found on this device';
                        solutions = 'Use manual verification below to verify tickets.';
                        break;
                        
                    case 'NotSupportedError':
                        message = 'Camera not supported in this browser';
                        solutions = 'Try Chrome, Firefox, or Safari for better camera support.';
                        break;
                        
                    case 'NotReadableError':
                        message = 'Camera is being used by another application';
                        solutions = `
                            <strong>Solutions:</strong><br>
                            1. Close other apps using the camera<br>
                            2. Restart your browser<br>
                            3. Try again
                        `;
                        break;
                        
                    default:
                        message = `Camera error: ${error.message}`;
                        solutions = `
                            <strong>Try these steps:</strong><br>
                            1. Refresh the page<br>
                            2. Check camera permissions<br>
                            3. Try a different browser<br>
                            4. Use manual verification below
                        `;
                }
                
                const troubleshootingHTML = `
                    <div style="background: rgba(239, 68, 68, 0.1); padding: 20px; border-radius: 12px; border: 1px solid rgba(239, 68, 68, 0.3);">
                        <h3 style="color: #ef4444; margin-bottom: 15px;">📷 Camera Issue</h3>
                        <p style="margin-bottom: 15px;"><strong>${message}</strong></p>
                        <div style="text-align: left;">${solutions}</div>
                        
                        <div style="margin-top: 20px; padding: 15px; background: rgba(99, 102, 241, 0.1); border-radius: 8px;">
                            <strong>💡 Tip:</strong> Manual verification works without camera access. Scroll down to use it.
                        </div>
                    </div>
                `;
                
                showResult(troubleshootingHTML, 'error');
                
                // Auto-scroll to manual verification
                setTimeout(() => {
                    document.querySelector('.manual-entry').scrollIntoView({ 
                        behavior: 'smooth',
                        block: 'start'
                    });
                }, 1000);
            }
        }
        
        // Global instance
        const mobileCamera = new MobileCameraHelper();
    