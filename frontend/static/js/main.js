/**
 * DERMAVISION_CORE - GLOBAL INTERFACE CONTROLLER
 * Manages State, UI Animations, and Neural AI Bridge
 */

const DermaVision = {
    // Global State
    state: {
        isPanelOpen: false,
        lastAnalysis: null,
        isVocalEnabled: false
    },

    /**
     * INITIALIZATION: Boot up global listeners
     */
    init() {
        console.log("🚀 NEURAL_CORE: ONLINE");
        this.bindEvents();
        this.applyGlassMorphismEffects();
        this.bootParticleBackground();
    },

    bindEvents() {
        // AI Panel Toggle
        const aiTrigger = document.getElementById('ai-trigger');
        if (aiTrigger) {
            aiTrigger.addEventListener('click', () => this.toggleAIPanel());
        }

        // Global Keyboard HUD Shortcuts
        document.addEventListener('keydown', (e) => {
            if (e.key === '`') this.toggleAIPanel(); // Tilde to quick-toggle AI
        });

        // Smooth Scroll for Clinical Dashboards
        document.querySelectorAll('a[href^="#"]').forEach(anchor => {
            anchor.addEventListener('click', function (e) {
                e.preventDefault();
                const targetElement = document.querySelector(this.getAttribute('href'));
                if (targetElement) {
                    targetElement.scrollIntoView({
                        behavior: 'smooth'
                    });
                }
            });
        });

        // "TRANSMIT" Input Form Listener Setup
        const chatInput = document.getElementById('ai-input');
        const transmitBtn = document.querySelector('.transmit-btn');
        
        if (transmitBtn && chatInput) {
            transmitBtn.addEventListener('click', () => {
                const message = chatInput.value.trim();
                if (message) {
                    this.sendChatMessage(message);
                    chatInput.value = '';
                }
            });
            
            chatInput.addEventListener('keydown', (e) => {
                if (e.key === 'Enter') {
                    const message = chatInput.value.trim();
                    if (message) {
                        this.sendChatMessage(message);
                        chatInput.value = '';
                    }
                }
            });
        }
    },

    /**
     * UI TRANSITIONS: Cinematic Panel Movements
     */
    toggleAIPanel() {
        const panel = document.getElementById('ai-panel');
        const trigger = document.getElementById('ai-trigger');
        
        if (!panel) return;
        
        this.state.isPanelOpen = !this.state.isPanelOpen;

        if (this.state.isPanelOpen) {
            panel.style.display = 'flex';
            // Cinematic Slide Up
            panel.animate([
                { transform: 'translateY(30px) scale(0.95)', opacity: 0 },
                { transform: 'translateY(0) scale(1)', opacity: 1 }
            ], { duration: 400, easing: 'cubic-bezier(0.2, 1, 0.3, 1)', fill: 'forwards' });
            
            if (trigger) trigger.style.transform = 'rotate(90deg)';
        } else {
            // Cinematic Slide Down
            const anim = panel.animate([
                { transform: 'translateY(0) scale(1)', opacity: 1 },
                { transform: 'translateY(30px) scale(0.95)', opacity: 0 }
            ], { duration: 300, easing: 'ease-in', fill: 'forwards' });
            
            anim.onfinish = () => panel.style.display = 'none';
            if (trigger) trigger.style.transform = 'rotate(0deg)';
        }
    },

    /**
     * CHAT TELEMETRY: Sending queries to the backend API blueprint pipeline
     */
    async sendChatMessage(message) {
        const flow = document.getElementById('chat-flow');
        const status = document.getElementById('ai-status-text');

        if (!flow) return;

        // Append User Bubble
        this.appendMessage('user', message);
        
        if (status) status.innerText = "● ANALYZING_DATA";

        try {
            // FIXED: Point to the verified API blueprint prefix route matching backend/routes/api_routes.py
            const response = await fetch('/api/chatbot/query', {
                method: 'POST',
                credentials: 'include',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message: message })
            });

            if (!response.ok) {
                throw new Error(`HTTP network error status: ${response.status}`);
            }

            const data = await response.json();
            
            // FIXED: Read data.verdict to align seamlessly with backend API json keys
            if (data.status === "SUCCESS") {
                this.appendMessage('ai', data.verdict);
            } else {
                this.appendMessage('ai', `SYSTEM_REJECTION: ${data.message || 'Malformed payload routing.'}`);
            }
        } catch (error) {
            console.error("[FRONTEND ERROR]", error);
            this.appendMessage('ai', "SYSTEM_ERROR: Neural bridge offline. Check server connection parameters.");
        }

        if (status) status.innerText = "● CORE_READY";
        flow.scrollTop = flow.scrollHeight;
    },

    appendMessage(role, text) {
        const flow = document.getElementById('chat-flow');
        if (!flow) return;

        const msgDiv = document.createElement('div');
        msgDiv.className = `msg msg-${role}`;
        
        const label = role === 'ai' ? '[NEURAL_VERDICT]' : '[USER_QUERY]';
        const color = role === 'ai' ? 'var(--accent)' : '#888';

        msgDiv.innerHTML = `
            <span style="color: ${color}; font-weight: 800; font-size: 0.65rem; display: block; margin-bottom: 5px;">${label}</span>
            <p style="margin: 0; line-height: 1.4;">${text}</p>
        `;
        
        flow.appendChild(msgDiv);
        flow.scrollTop = flow.scrollHeight;
    },

    /**
     * PREMIUM UX: Particle Background Logic
     */
    bootParticleBackground() {
        console.log("🌌 Background Dynamics: Initialized");
    },

    applyGlassMorphismEffects() {
        window.addEventListener('scroll', () => {
            const nav = document.querySelector('.navbar');
            if (!nav) return;
            if (window.scrollY > 50) {
                nav.style.background = 'rgba(8, 8, 8, 0.95)';
                nav.style.borderBottom = '1px solid rgba(226, 88, 34, 0.2)';
            } else {
                nav.style.background = 'transparent';
                nav.style.borderBottom = '1px solid rgba(255, 255, 255, 0.05)';
            }
        });
    }
};

// Start the Core
document.addEventListener('DOMContentLoaded', () => DermaVision.init());

/**
 * UTILITY: Handle Global Transmissions
 * This allows other scripts (like scanner.js) to trigger AI messages
 */
window.transmitToAI = (msg) => DermaVision.sendChatMessage(msg);