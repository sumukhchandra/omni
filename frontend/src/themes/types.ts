export interface ThemeConfig {
    colors: {
        background: string;
        particle: string;
        line: string;
    };
    params: {
        baseAlpha: number;
        highlightAlpha: number; // For mouse interaction
        connectionDistance: number;
        densityDivider: number; // Higher = fewer particles
        lineOpacityMultiplier: number;
        particleSizeMin: number;
        particleSizeMax: number;
        speedMultiplier: number; // 1.0 is default
    };
}

export interface Theme {
    id: string;
    name: string;
    light: ThemeConfig;
    dark: ThemeConfig;
}

export type ThemeId = string;
