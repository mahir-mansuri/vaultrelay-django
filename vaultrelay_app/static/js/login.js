const glitchTitle = document.querySelector('.cyber-glitch');
        glitchTitle.addEventListener('mouseenter', () => {
            glitchTitle.classList.add('glitch-active');
            setTimeout(() => glitchTitle.classList.remove('glitch-active'), 500);
        });

        // Particle Explosion on Button Click
        const cyberBtn = document.querySelector('.cyber-button');
        cyberBtn.addEventListener('click', (e) => {
            e.preventDefault();
            const explosion = cyberBtn.querySelector('.cyber-btn-explosion');
            explosion.style.opacity = '1';
            explosion.style.transform = 'scale(1)';
            
            setTimeout(() => {
                explosion.style.opacity = '0';
                explosion.style.transform = 'scale(0)';
                cyberBtn.closest('form').submit(); // Submit form after animation
            }, 800);
        });

        // Floating Particles Background
        const particleContainer = document.querySelector('.cyber-particles');
        for (let i = 0; i < 50; i++) {
            const particle = document.createElement('div');
            particle.classList.add('cyber-particle');
            
            particle.style.left = `${Math.random() * 100}%`;
            particle.style.top = `${Math.random() * 100}%`;
            particle.style.width = `${Math.random() * 4 + 2}px`;
            particle.style.height = particle.style.width;
            particle.style.animationDelay = `${Math.random() * 5}s`;
            
            particleContainer.appendChild(particle);
        }