
(function () {
    function init() {
        // 1. Inject CSS
        const style = document.createElement('style');
        style.innerHTML = `
            .lead-modal-overlay {
                position: fixed; top: 0; left: 0; width: 100%; height: 100%;
                background: rgba(0,0,0,0.8); z-index: 9999;
                display: none; align-items: center; justify-content: center;
                backdrop-filter: blur(5px);
                -webkit-backdrop-filter: blur(5px);
            }
            .lead-modal {
                background: #111; border: 1px solid #333; padding: 32px;
                border-radius: 16px; width: 90%; max-width: 400px;
                position: relative;
                box-shadow: 0 20px 50px rgba(0,0,0,0.5);
            }
            .lead-modal h2 { margin-top: 0; color: white; margin-bottom: 8px; }
            .lead-modal p { color: #999; margin-bottom: 24px; font-size: 14px; }
            .lead-input {
                width: 100%; padding: 12px; margin-bottom: 16px;
                background: #222; border: 1px solid #444; color: white;
                border-radius: 8px; font-size: 16px;
            }
            .lead-btn {
                width: 100%; padding: 14px; background: #dc2626; color: white;
                border: none; border-radius: 8px; font-size: 16px; font-weight: bold;
                cursor: pointer; transition: 0.2s;
            }
            .lead-btn:hover { background: #b91c1c; }
            .close-modal {
                position: absolute; top: 16px; right: 16px; color: #666; cursor: pointer; font-size: 20px;
            }
        `;
        document.head.appendChild(style);

        // 2. Inject HTML
        const modalHTML = `
            <div class="lead-modal-overlay" id="leadModal">
                <div class="lead-modal">
                    <span class="close-modal">&times;</span>
                    <h2>Start Process</h2>
                    <p>Enter your details to initiate the AI dispatch system.</p>
                    <form id="leadForm">
                        <input type="text" class="lead-input" name="name" placeholder="Business Name" required>
                        <input type="tel" class="lead-input" name="phone" placeholder="Phone Number" required>
                        <input type="email" class="lead-input" name="email" placeholder="Email Address" required>
                        
                        <div style="margin-bottom: 16px; display: flex; align-items: flex-start; gap: 8px; font-size: 12px; color: #999;">
                            <input type="checkbox" id="complianceCheck" required style="margin-top: 2px;">
                            <label for="complianceCheck">
                                I agree to the <a href="#" style="color: #dc2626;">Terms of Service</a> and 
                                <a href="#" style="color: #dc2626;">Privacy Policy</a>. I give permission to be contacted 
                                via automated SMS and Voice calls.
                            </label>
                        </div>

                        <button type="submit" class="lead-btn">Activate System</button>
                    </form>
                </div>
            </div>
        `;
        const div = document.createElement('div');
        div.innerHTML = modalHTML;
        document.body.appendChild(div);

        // 3. Elements
        const modal = document.getElementById('leadModal');
        const close = document.querySelector('.close-modal');
        const form = document.getElementById('leadForm');

        // 4. Open Logic
        function openModal(e) {
            if (e && e.preventDefault) e.preventDefault();
            modal.style.display = 'flex';
        }

        // Expose globally for onclick handlers in HTML
        window.openModal = openModal;
        window.openFunnel = openModal;

        function closeModal() {
            modal.style.display = 'none';
        }

        // Bind to existing buttons
        const triggers = document.querySelectorAll('.btn, .btn-primary, .header-cta');
        triggers.forEach(btn => {
            btn.addEventListener('click', openModal);
            if (btn.getAttribute('href') && (btn.getAttribute('href').includes('{') || btn.getAttribute('href') === '#')) {
                btn.setAttribute('href', 'javascript:void(0)');
            }
        });

        if (close) close.addEventListener('click', closeModal);

        // 5. Submit Logic
        if (form) {
            form.addEventListener('submit', async (e) => {
                e.preventDefault();

                const checkbox = document.getElementById('complianceCheck');
                if (!checkbox.checked) {
                    alert("You must agree to the Terms and Privacy Policy to proceed.");
                    return;
                }

                const btn = form.querySelector('button');
                const originalText = btn.innerText;
                btn.innerText = "Processing...";
                btn.disabled = true;

                const formData = new FormData(form);
                const data = {
                    name: formData.get('name'),
                    phone: formData.get('phone'),
                    email: formData.get('email'),
                    industry: document.title
                };

                try {
                    const res = await fetch('/api/leads', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify(data)
                    });

                    if (res.ok) {
                        btn.style.background = '#22c55e';
                        btn.innerText = "Success! Check Dashboard.";
                        setTimeout(() => {
                            closeModal();
                            form.reset();
                            btn.innerText = originalText;
                            btn.style.background = '#dc2626';
                            btn.disabled = false;
                        }, 2000);
                    } else {
                        throw new Error("Failed");
                    }
                } catch (err) {
                    alert("System Error. Please call the number in the header.");
                    btn.innerText = originalText;
                    btn.disabled = false;
                }
            });
        }
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }

})();
