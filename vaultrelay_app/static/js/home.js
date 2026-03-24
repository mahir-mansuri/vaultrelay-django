document.addEventListener("DOMContentLoaded", function () {

    /* ===============================
       CYBER GLITCH EFFECT
    =============================== */
    const glitchTitle = document.querySelector('.cyber-glitch');
    if (glitchTitle) {
        glitchTitle.addEventListener('mouseenter', () => {
            glitchTitle.classList.add('glitch-active');
            setTimeout(() => glitchTitle.classList.remove('glitch-active'), 500);

            // Create glitch particles
            for (let i = 0; i < 10; i++) {
                const particle = document.createElement('span');
                particle.className = 'glitch-particle';
                particle.style.left = `${Math.random() * glitchTitle.offsetWidth}px`;
                particle.style.top = `${Math.random() * glitchTitle.offsetHeight}px`;
                glitchTitle.appendChild(particle);

                setTimeout(() => particle.remove(), 300);
            }
        });
    }

    /* ===============================
       PARTICLE BACKGROUND EFFECT
    =============================== */
    const canvas = document.getElementById('particles-canvas');
    if (canvas) {
        const ctx = canvas.getContext('2d');
        let W = canvas.width = innerWidth;
        let H = canvas.height = innerHeight;

        window.addEventListener('resize', () => {
            W = canvas.width = innerWidth;
            H = canvas.height = innerHeight;
            initParticles();
        });

        const particles = [];
        const particleCount = 100;

        function initParticles() {
            particles.length = 0;
            for (let i = 0; i < particleCount; i++) {
                particles.push({
                    x: Math.random() * W,
                    y: Math.random() * H,
                    r: Math.random() * 3 + 1,
                    dx: (Math.random() - 0.5) * 2,
                    dy: (Math.random() - 0.5) * 2
                });
            }
        }

        function drawParticles() {
            ctx.clearRect(0, 0, W, H);
            ctx.fillStyle = 'rgba(0, 255, 255, 0.7)';
            ctx.beginPath();
            particles.forEach(p => {
                ctx.moveTo(p.x, p.y);
                ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2, true);
            });
            ctx.fill();
            updateParticles();
        }

        function updateParticles() {
            particles.forEach(p => {
                p.x += p.dx;
                p.y += p.dy;
                if (p.x < 0 || p.x > W) p.dx *= -1;
                if (p.y < 0 || p.y > H) p.dy *= -1;
            });
        }

        function animateParticles() {
            drawParticles();
            requestAnimationFrame(animateParticles);
        }

        initParticles();
        animateParticles();
    }

});
