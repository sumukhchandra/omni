import React, { useEffect, useRef } from 'react';
import { themes, defaultThemeId, ThemeId } from '../src/themes';

interface CrystalBackgroundProps {
    theme?: 'light' | 'dark';
    themeId?: ThemeId;
}

const CrystalBackground: React.FC<CrystalBackgroundProps> = ({ theme = 'light', themeId = defaultThemeId }) => {
    const canvasRef = useRef<HTMLCanvasElement>(null);

    useEffect(() => {
        const canvas = canvasRef.current;
        if (!canvas) return;

        const ctx = canvas.getContext('2d');
        if (!ctx) return;

        // Resolve Theme Config
        const selectedTheme = themes.find(t => t.id === themeId) || themes.find(t => t.id === defaultThemeId)!;
        const config = theme === 'dark' ? selectedTheme.dark : selectedTheme.light;

        let width = window.innerWidth;
        let height = window.innerHeight;
        let particles: Particle[] = [];
        let cursorParticles: Particle[] = [];
        let mouse = { x: -1000, y: -1000 };

        canvas.width = width;
        canvas.height = height;

        class Particle {
            x: number;
            y: number;
            size: number;
            vx: number;
            vy: number;
            baseAlpha: number;
            pulse: number;
            pulseSpeed: number;
            life: number;
            isCursor: boolean;

            constructor(x?: number, y?: number, isCursor: boolean = false) {
                this.x = x ?? Math.random() * width;
                this.y = y ?? Math.random() * height;
                this.isCursor = isCursor;

                if (isCursor) {
                    this.size = Math.random() * 2 + 0.5;
                    this.vx = (Math.random() - 0.5) * 1;
                    this.vy = (Math.random() - 0.5) * 1;
                    this.baseAlpha = config.params.highlightAlpha;
                    this.life = 1.0;
                } else {
                    this.size = Math.random() * (config.params.particleSizeMax - config.params.particleSizeMin) + config.params.particleSizeMin;
                    this.vx = (Math.random() - 0.5) * config.params.speedMultiplier;
                    this.vy = (Math.random() - 0.5) * config.params.speedMultiplier;
                    // Let's keep some variation but based on the theme base
                    this.baseAlpha = config.params.baseAlpha * (0.5 + Math.random() * 0.5);
                    this.life = 100;
                }

                this.pulse = Math.random() * Math.PI;
                this.pulseSpeed = 0.05 + Math.random() * 0.05;
            }

            update() {
                this.x += this.vx;
                this.y += this.vy;
                this.pulse += this.pulseSpeed;

                if (this.isCursor) {
                    this.life -= 0.02;
                } else {
                    if (this.x < 0) this.x = width;
                    if (this.x > width) this.x = 0;
                    if (this.y < 0) this.y = height;
                    if (this.y > height) this.y = 0;
                }
            }

            draw(ctx: CanvasRenderingContext2D) {
                const dx = mouse.x - this.x;
                const dy = mouse.y - this.y;
                const distance = Math.sqrt(dx * dx + dy * dy);
                const maxDist = 250;

                let alpha = this.baseAlpha;
                let scale = 1;

                if (this.isCursor) {
                    alpha = this.life;
                } else {
                    alpha += Math.sin(this.pulse) * 0.05;
                    if (distance < maxDist) {
                        const factor = (maxDist - distance) / maxDist;
                        alpha += factor * (config.params.highlightAlpha - alpha); // Blend towards highlight
                        scale += factor * 1.5;
                    }
                }

                // Hard clamp
                alpha = Math.min(Math.max(alpha, 0), 1);

                if (alpha <= 0.01) return;

                ctx.beginPath();
                ctx.arc(this.x, this.y, this.size * scale, 0, Math.PI * 2);
                ctx.fillStyle = `${config.colors.particle}${alpha})`;
                ctx.fill();

                // Connections
                const allParticles = [...particles, ...cursorParticles];
                allParticles.forEach(p2 => {
                    if (p2 === this) return;

                    const dx2 = this.x - p2.x;
                    const dy2 = this.y - p2.y;
                    const dist2 = Math.sqrt(dx2 * dx2 + dy2 * dy2);

                    if (dist2 < config.params.connectionDistance) {
                        ctx.beginPath();
                        const lineAlpha = (1 - dist2 / config.params.connectionDistance) * alpha * config.params.lineOpacityMultiplier;

                        if (lineAlpha > 0.02) {
                            ctx.strokeStyle = `${config.colors.line}${lineAlpha})`;
                            ctx.lineWidth = 0.8;
                            ctx.moveTo(this.x, this.y);
                            ctx.lineTo(p2.x, p2.y);
                            ctx.stroke();
                        }
                    }
                });
            }
        }

        const init = () => {
            particles = [];
            cursorParticles = [];
            const particleCount = Math.floor((width * height) / config.params.densityDivider);
            for (let i = 0; i < particleCount; i++) {
                particles.push(new Particle(undefined, undefined, false));
            }
        };

        const animate = () => {
            if (!ctx || !canvasRef.current) return;
            ctx.clearRect(0, 0, width, height);

            particles.forEach(p => {
                p.update();
                p.draw(ctx);
            });

            for (let i = cursorParticles.length - 1; i >= 0; i--) {
                const p = cursorParticles[i];
                p.update();
                if (p.life <= 0) {
                    cursorParticles.splice(i, 1);
                } else {
                    p.draw(ctx);
                }
            }
            requestAnimationFrame(animate);
        };

        const handleResize = () => {
            width = window.innerWidth;
            height = window.innerHeight;
            canvas.width = width;
            canvas.height = height;
            init();
        };

        const handleMouseMove = (e: MouseEvent) => {
            mouse.x = e.clientX;
            mouse.y = e.clientY;

            // Spawn particles
            for (let i = 0; i < 3; i++) {
                cursorParticles.push(new Particle(mouse.x + (Math.random() - 0.5) * 10, mouse.y + (Math.random() - 0.5) * 10, true));
            }
            if (cursorParticles.length > 200) {
                cursorParticles.splice(0, cursorParticles.length - 200);
            }
        };

        window.addEventListener('resize', handleResize);
        window.addEventListener('mousemove', handleMouseMove);

        init();
        const animationId = requestAnimationFrame(animate);

        return () => {
            window.removeEventListener('resize', handleResize);
            window.removeEventListener('mousemove', handleMouseMove);
            cancelAnimationFrame(animationId);
        };
    }, [theme, themeId]);

    return (
        <canvas
            ref={canvasRef}
            className="fixed inset-0 pointer-events-none z-0 transition-opacity duration-1000"
        />
    );
};

export default CrystalBackground;
