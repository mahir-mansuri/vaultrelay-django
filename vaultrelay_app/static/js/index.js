document.addEventListener("DOMContentLoaded", function () {
    // Cyber Glitch Effect
    const glitchTitle = document.querySelector('.cyber-glitch');
    if (glitchTitle) {
        glitchTitle.addEventListener('mouseenter', () => {
            glitchTitle.classList.add('glitch-active');
            setTimeout(() => glitchTitle.classList.remove('glitch-active'), 500);

            // Create glitch particles
            for (let i = 0; i < 10; i++) {
                const particle = document.createElement('div');
                particle.classList.add('cyber-particle');
                particle.style.position = 'absolute';
                particle.style.left = `${Math.random() * 100}%`;
                particle.style.top = `${Math.random() * 100}%`;
                particle.style.width = `${Math.random() * 4 + 2}px`;
                particle.style.height = particle.style.width;
                particle.style.animation = `floatParticle ${Math.random() * 2 + 1}s ease-in-out forwards`;
                particle.style.opacity = '0';

                const colors = ['#00f0ff', '#ff00aa', '#9d00ff', '#00ff88'];
                particle.style.background = colors[Math.floor(Math.random() * colors.length)];

                glitchTitle.appendChild(particle);

                gsap.to(particle, {
                    opacity: 0.8,
                    duration: 0.2,
                    onComplete: () => {
                        gsap.to(particle, {
                            opacity: 0,
                            duration: 0.5,
                            delay: 0.3,
                            onComplete: () => particle.remove()
                        });
                    }
                });
            }
        });
    }

    // Button Explosion Effect
    const cyberBtn = document.querySelector('.cyber-button');
    if (cyberBtn) {
        cyberBtn.addEventListener('click', () => {
            const explosion = cyberBtn.querySelector('.cyber-btn-explosion');
            explosion.style.opacity = '1';
            explosion.style.transform = 'translate(-50%, -50%) scale(1)';

            for (let i = 0; i < 20; i++) {
                const particle = document.createElement('div');
                particle.classList.add('cyber-particle');
                particle.style.position = 'absolute';
                particle.style.left = `${Math.random() * 100}%`;
                particle.style.top = `${Math.random() * 100}%`;
                particle.style.width = `${Math.random() * 6 + 3}px`;
                particle.style.height = particle.style.width;

                const colors = ['#00f0ff', '#ff00aa', '#9d00ff', '#00ff88'];
                particle.style.background = colors[Math.floor(Math.random() * colors.length)];

                cyberBtn.appendChild(particle);

                gsap.to(particle, {
                    x: (Math.random() - 0.5) * 200,
                    y: (Math.random() - 0.5) * 200,
                    opacity: 0,
                    duration: 1,
                    onComplete: () => particle.remove()
                });
            }

            setTimeout(() => {
                explosion.style.opacity = '0';
                explosion.style.transform = 'translate(-50%, -50%) scale(0)';
            }, 800);
        });
    }

    // Password Strength Checker
    const passwordInput = document.querySelector("input[name='pass1']");
    const strengthBar = document.querySelector(".progress-bar");
    const strengthText = document.getElementById("strength-text");

    if (passwordInput && strengthBar && strengthText) {
        passwordInput.addEventListener("input", function () {
            const password = this.value;
            let strength = 0;

            if (password.length >= 8) strength += 1;
            if (password.length >= 12) strength += 1;
            if (/[A-Z]/.test(password)) strength += 1;
            if (/[0-9]/.test(password)) strength += 1;
            if (/[^A-Za-z0-9]/.test(password)) strength += 1;

            let width = 0;
            let color = "bg-danger";
            let text = "Weak";

            if (strength >= 4) {
                width = 75;
                color = "bg-warning";
                text = "Good";
            }
            if (strength >= 5) {
                width = 100;
                color = "bg-success";
                text = "Strong";
            } else if (strength >= 3) {
                width = 50;
                color = "bg-info";
                text = "Medium";
            }

            strengthBar.style.width = `${width}%`;
            strengthBar.className = `progress-bar ${color}`;
            strengthText.textContent = text;

            strengthBar.style.transform = "scaleX(1.1)";
            setTimeout(() => {
                strengthBar.style.transform = "scaleX(1)";
            }, 300);
        });
    }

    // Create floating particles
    const particleContainer = document.querySelector('.cyber-particles');
    if (particleContainer) {
        for (let i = 0; i < 100; i++) {
            const particle = document.createElement('div');
            particle.classList.add('cyber-particle');
            particle.style.left = `${Math.random() * 100}%`;
            particle.style.top = `${Math.random() * 100}%`;
            const size = Math.random() * 4 + 1;
            particle.style.width = `${size}px`;
            particle.style.height = `${size}px`;
            particle.style.animation = `floatParticle ${Math.random() * 15 + 5}s ease-in-out infinite`;
            particle.style.animationDelay = `${Math.random() * 5}s`;

            const colors = ['#00f0ff', '#ff00aa', '#9d00ff', '#00ff88'];
            particle.style.background = colors[Math.floor(Math.random() * colors.length)];

            particleContainer.appendChild(particle);
        }
    }

    // Form validation
    const form = document.querySelector("form");
    if (form) {
        form.addEventListener("submit", function (event) {
            const password = document.querySelector("input[name='pass1']").value;
            const confirmPassword = document.querySelector("input[name='pass2']").value;
            const regex = /^(?=.*[A-Z])(?=.*\d)(?=.*[!@#$%^&*()_+=\[\]{}|\\:;"',.<>?/`~-]).{6,}$/;

            if (password !== confirmPassword) {
                alert("Passwords do not match!");
                event.preventDefault();
                return;
            }

            if (!regex.test(password)) {
                alert("Password must be at least 6 characters with one uppercase, one number, and one special character.");
                event.preventDefault();
                return;
            }

            const submitBtn = document.querySelector('.cyber-button');
        if (submitBtn) {
            submitBtn.innerHTML = '<span class="cyber-btn-text"><i class="fas fa-spinner fa-spin"></i> PROCESSING...</span>';
            submitBtn.disabled = true;
        }
        });
    }

    // Input focus effects
    document.querySelectorAll('.cyber-input-field').forEach(input => {
        input.addEventListener('focus', function () {
            this.parentElement.style.transform = 'scale(1.02)';
        });
        input.addEventListener('blur', function () {
            this.parentElement.style.transform = 'scale(1)';
        });
    });

    // Initialize GSAP animations
    if (typeof gsap !== "undefined") {
        gsap.from('.vault-form', {
            duration: 1.5,
            y: 50,
            opacity: 0,
            ease: "power2.out"
        });

        gsap.from('.cyber-input', {
            duration: 0.8,
            y: 30,
            opacity: 0,
            stagger: 0.1,
            ease: "power2.out",
            delay: 0.5
        });
    }
});
