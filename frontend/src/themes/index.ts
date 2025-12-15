export * from './types';
import { Theme } from './types';

export const CrystalTheme: Theme = {
    id: 'crystal',
    name: 'Crystal (Default)',
    light: {
        colors: {
            background: 'transparent',
            particle: 'rgba(59, 130, 246, ', // Blue
            line: 'rgba(59, 130, 246, ' // Blue
        },
        params: {
            baseAlpha: 0.3, // Boosted light mode opacity
            highlightAlpha: 0.5,
            connectionDistance: 150,
            densityDivider: 9000,
            lineOpacityMultiplier: 1.0,
            particleSizeMin: 1,
            particleSizeMax: 3,
            speedMultiplier: 0.3
        }
    },
    dark: {
        colors: {
            background: 'transparent',
            particle: 'rgba(255, 255, 255, ', // White
            line: 'rgba(255, 255, 255, ' // White
        },
        params: {
            baseAlpha: 0.5, // Boosted dark mode opacity
            highlightAlpha: 0.8,
            connectionDistance: 150,
            densityDivider: 9000,
            lineOpacityMultiplier: 1.0, // Full opacity lines
            particleSizeMin: 1,
            particleSizeMax: 3,
            speedMultiplier: 0.3
        }
    }
};

export const NeonTheme: Theme = {
    id: 'neon',
    name: 'Neon Cyberpunk',
    light: {
        colors: {
            background: 'transparent',
            particle: 'rgba(236, 72, 153, ', // Pink
            line: 'rgba(168, 85, 247, ' // Purple
        },
        params: {
            baseAlpha: 0.4,
            highlightAlpha: 0.7,
            connectionDistance: 160,
            densityDivider: 8000,
            lineOpacityMultiplier: 1.2,
            particleSizeMin: 1.5,
            particleSizeMax: 4,
            speedMultiplier: 0.5
        }
    },
    dark: {
        colors: {
            background: 'transparent',
            particle: 'rgba(34, 211, 238, ', // Cyan
            line: 'rgba(236, 72, 153, ' // Pink
        },
        params: {
            baseAlpha: 0.6,
            highlightAlpha: 1.0,
            connectionDistance: 160,
            densityDivider: 8000,
            lineOpacityMultiplier: 1.2,
            particleSizeMin: 1.5,
            particleSizeMax: 4,
            speedMultiplier: 0.5
        }
    }
};

export const themes: Theme[] = [CrystalTheme, NeonTheme];
export const defaultThemeId = 'crystal';
