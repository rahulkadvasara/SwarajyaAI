/**
 * SwarajyaAI Frontend JavaScript
 * Handles voice recognition, text-to-speech, and API communication
 * 
 * Key Features:
 * - Web Speech API integration for voice input/output
 * - FastAPI backend communication
 * - Error handling and user feedback
 * - Responsive UI updates
 * 
 * TODO: Add these enhancements later:
 * - Language selection dropdown
 * - Voice settings (speed, pitch)
 * - Query history
 * - Offline support
 * - User preferences storage
 */

class SwarajyaAI {
    constructor() {
        // API Configuration - Update this URL for production
        this.API_BASE_URL = 'http://localhost:8000';
        
        // Speech Recognition setup
        this.recognition = null;
        this.synthesis = window.speechSynthesis;
        this.isListening = false;
        this.isProcessing = false;
        this.currentUtterance = null;
        
        // DOM Elements
        this.micButton = document.getElementById('micButton');
        this.micStatus = document.getElementById('micStatus');
        this.listeningIndicator = document.getElementById('listeningIndicator');
        this.processingIndicator = document.getElementById('processingIndicator');
        this.queryDisplay = document.getElementById('queryDisplay');
        this.queryText = document.getElementById('queryText');
        this.responseSection = document.getElementById('responseSection');
        this.responseText = document.getElementById('responseText');
        this.responseLink = document.getElementById('responseLink');
        this.schemeLink = document.getElementById('schemeLink');
        this.playButton = document.getElementById('playButton');
        this.stopButton = document.getElementById('stopButton');
        this.errorModal = document.getElementById('errorModal');
        this.errorMessage = document.getElementById('errorMessage');
        this.closeError = document.getElementById('closeError');
        
        // Initialize the application
        this.init();
    }
    
    /**
     * Initialize the application
     * Set up event listeners and check browser compatibility
     */
    init() {
        console.log('Initializing SwarajyaAI...');
        
        // Check browser compatibility
        if (!this.checkBrowserSupport()) {
            this.showError('आपका ब्राउज़र voice recognition को support नहीं करता। कृपया Chrome या Firefox का उपयोग करें।');
            return;
        }
        
        // Set up speech recognition
        this.setupSpeechRecognition();
        
        // Set up event listeners
        this.setupEventListeners();
        
        console.log('SwarajyaAI initialized successfully');
    }
    
    /**
     * Check if browser supports required APIs
     */
    checkBrowserSupport() {
        const hasWebSpeech = 'webkitSpeechRecognition' in window || 'SpeechRecognition' in window;
        const hasSpeechSynthesis = 'speechSynthesis' in window;
        
        return hasWebSpeech && hasSpeechSynthesis;
    }
    
    /**
     * Set up Web Speech API for voice recognition
     */
    setupSpeechRecognition() {
        // Create speech recognition instance
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        this.recognition = new SpeechRecognition();
        
        // Configure recognition settings
        this.recognition.continuous = false;          // Stop after one result
        this.recognition.interimResults = false;      // Only final results
        this.recognition.lang = 'hi-IN';             // Hindi (India) - change as needed
        this.recognition.maxAlternatives = 1;         // Single best result
        
        // Set up recognition event handlers
        this.recognition.onstart = () => {
            console.log('Speech recognition started');
            this.onListeningStart();
        };
        
        this.recognition.onresult = (event) => {
            const result = event.results[0][0].transcript;
            console.log('Speech recognition result:', result);
            this.onSpeechResult(result);
        };
        
        this.recognition.onerror = (event) => {
            console.error('Speech recognition error:', event.error);
            this.onSpeechError(event.error);
        };
        
        this.recognition.onend = () => {
            console.log('Speech recognition ended');
            this.onListeningEnd();
        };
    }
    
    /**
     * Set up all event listeners
     */
    setupEventListeners() {
        // Microphone button click
        this.micButton.addEventListener('click', () => {
            this.toggleListening();
        });
        
        // Audio control buttons
        this.playButton.addEventListener('click', () => {
            this.playResponse();
        });
        
        this.stopButton.addEventListener('click', () => {
            this.stopSpeech();
        });
        
        // Error modal close
        this.closeError.addEventListener('click', () => {
            this.hideError();
        });
        
        // Example query buttons
        const exampleButtons = document.querySelectorAll('.example-btn');
        exampleButtons.forEach(button => {
            button.addEventListener('click', () => {
                const query = button.getAttribute('data-query');
                this.processTextQuery(query);
            });
        });
        
        // Keyboard shortcuts
        document.addEventListener('keydown', (event) => {
            // Space bar to toggle listening
            if (event.code === 'Space' && !event.target.matches('input, textarea')) {
                event.preventDefault();
                this.toggleListening();
            }
            
            // Escape to stop speech
            if (event.code === 'Escape') {
                this.stopSpeech();
                this.hideError();
            }
        });
    }
    
    /**
     * Toggle voice listening on/off
     */
    toggleListening() {
        if (this.isListening) {
            this.stopListening();
        } else {
            this.startListening();
        }
    }
    
    /**
     * Start voice recognition
     */
    startListening() {
        if (this.isProcessing) {
            this.showError('कृपया प्रतीक्षा करें, पिछला query process हो रहा है।');
            return;
        }
        
        try {
            this.recognition.start();
        } catch (error) {
            console.error('Error starting recognition:', error);
            this.showError('Voice recognition शुरू नहीं हो सका। कृपया फिर से कोशिश करें।');
        }
    }
    
    /**
     * Stop voice recognition
     */
    stopListening() {
        if (this.recognition && this.isListening) {
            this.recognition.stop();
        }
    }
    
    /**
     * Handle listening start
     */
    onListeningStart() {
        this.isListening = true;
        this.micButton.classList.add('listening');
        this.micStatus.textContent = 'बोलिए...';
        this.listeningIndicator.classList.remove('hidden');
        this.hideAllSections();
    }
    
    /**
     * Handle listening end
     */
    onListeningEnd() {
        this.isListening = false;
        this.micButton.classList.remove('listening');
        this.micStatus.textContent = 'माइक दबाएं और बोलें';
        this.listeningIndicator.classList.add('hidden');
    }
    
    /**
     * Handle speech recognition result
     */
    onSpeechResult(transcript) {
        this.displayQuery(transcript);
        this.processTextQuery(transcript);
    }
    
    /**
     * Handle speech recognition errors
     */
    onSpeechError(error) {
        let errorMessage = 'Voice recognition में समस्या हुई।';
        
        switch (error) {
            case 'no-speech':
                errorMessage = 'कोई आवाज़ नहीं सुनाई दी। कृपया फिर से कोशिश करें।';
                break;
            case 'audio-capture':
                errorMessage = 'माइक्रोफोन access नहीं मिला। कृपया permission दें।';
                break;
            case 'not-allowed':
                errorMessage = 'माइक्रोफोन की permission नहीं दी गई।';
                break;
            case 'network':
                errorMessage = 'Network की समस्या। Internet connection check करें।';
                break;
        }
        
        this.showError(errorMessage);
        this.onListeningEnd();
    }
    
    /**
     * Display user query in UI
     */
    displayQuery(query) {
        this.queryText.textContent = query;
        this.queryDisplay.classList.remove('hidden');
    }
    
    /**
     * Process text query (from voice or example buttons)
     */
    async processTextQuery(query) {
        if (!query || query.trim() === '') {
            this.showError('कृपया कोई सवाल पूछें।');
            return;
        }
        
        // Show processing state
        this.showProcessing();
        
        try {
            // Send query to backend API
            const response = await this.sendQueryToAPI(query);
            
            // Display response
            this.displayResponse(response);
            
            // Read response aloud
            this.speakResponse(response.reply);
            
        } catch (error) {
            console.error('Error processing query:', error);
            this.showError('Server से जवाब नहीं मिला। कृपया बाद में कोशिश करें।');
        } finally {
            this.hideProcessing();
        }
    }
    
    /**
     * Send query to FastAPI backend
     */
    async sendQueryToAPI(query) {
        const response = await fetch(`${this.API_BASE_URL}/query`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ query: query })
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        return await response.json();
    }
    
    /**
     * Display API response in UI
     */
    displayResponse(response) {
        this.responseText.textContent = response.reply;
        
        // Show link if available
        if (response.link) {
            this.schemeLink.href = response.link;
            this.responseLink.classList.remove('hidden');
        } else {
            this.responseLink.classList.add('hidden');
        }
        
        this.responseSection.classList.remove('hidden');
    }
    
    /**
     * Use Text-to-Speech to read response
     */
    speakResponse(text) {
        // Stop any current speech
        this.stopSpeech();
        
        // Create new utterance
        this.currentUtterance = new SpeechSynthesisUtterance(text);
        
        // Configure speech settings
        this.currentUtterance.lang = 'hi-IN';        // Hindi voice
        this.currentUtterance.rate = 0.9;            // Slightly slower for clarity
        this.currentUtterance.pitch = 1.0;           // Normal pitch
        this.currentUtterance.volume = 1.0;          // Full volume
        
        // Set up speech event handlers
        this.currentUtterance.onstart = () => {
            console.log('Speech synthesis started');
        };
        
        this.currentUtterance.onend = () => {
            console.log('Speech synthesis ended');
            this.currentUtterance = null;
        };
        
        this.currentUtterance.onerror = (event) => {
            console.error('Speech synthesis error:', event.error);
        };
        
        // Start speaking
        this.synthesis.speak(this.currentUtterance);
    }
    
    /**
     * Play the current response again
     */
    playResponse() {
        const responseText = this.responseText.textContent;
        if (responseText) {
            this.speakResponse(responseText);
        }
    }
    
    /**
     * Stop current speech synthesis
     */
    stopSpeech() {
        if (this.synthesis.speaking) {
            this.synthesis.cancel();
        }
        this.currentUtterance = null;
    }
    
    /**
     * Show processing state
     */
    showProcessing() {
        this.isProcessing = true;
        this.micButton.classList.add('processing');
        this.micStatus.textContent = 'प्रोसेसिंग...';
        this.processingIndicator.classList.remove('hidden');
    }
    
    /**
     * Hide processing state
     */
    hideProcessing() {
        this.isProcessing = false;
        this.micButton.classList.remove('processing');
        this.micStatus.textContent = 'माइक दबाएं और बोलें';
        this.processingIndicator.classList.add('hidden');
    }
    
    /**
     * Hide all result sections
     */
    hideAllSections() {
        this.queryDisplay.classList.add('hidden');
        this.responseSection.classList.add('hidden');
    }
    
    /**
     * Show error message to user
     */
    showError(message) {
        this.errorMessage.textContent = message;
        this.errorModal.classList.remove('hidden');
    }
    
    /**
     * Hide error modal
     */
    hideError() {
        this.errorModal.classList.add('hidden');
    }
}

// Initialize the application when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    // Create global instance
    window.swarajyaAI = new SwarajyaAI();
    
    // Add some helpful console messages for developers
    console.log('🇮🇳 SwarajyaAI Voice Assistant Loaded');
    console.log('💡 Press Space to start listening');
    console.log('💡 Press Escape to stop speech');
    console.log('🔧 Modify API_BASE_URL in script.js for production');
});

// Service Worker registration for future PWA support
// TODO: Implement service worker for offline functionality
if ('serviceWorker' in navigator) {
    window.addEventListener('load', () => {
        // navigator.serviceWorker.register('/sw.js')
        //     .then(registration => console.log('SW registered'))
        //     .catch(error => console.log('SW registration failed'));
    });
}