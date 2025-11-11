/**
 * Crypto KZ Color DNA - закрепленная триада
 * Persian Green - технологии: цифровая опора и навигация
 * Solar - люди: тепло, забота и поддержка
 * Cloud - традиции: честность и прозрачность
 */

import { Platform } from 'react-native';

// Crypto KZ Brand Colors
export const CryptoKZColors = {
  persianGreen: '#2D9A86',
  solar: '#EEFE6D',
  cloud: '#F5F9F8',
  white: '#FFFFFF',
  black: '#1A1A1A',
  gray: {
    50: '#F9FAFB',
    100: '#F3F4F6',
    200: '#E5E7EB',
    300: '#D1D5DB',
    400: '#9CA3AF',
    500: '#6B7280',
    600: '#4B5563',
    700: '#374151',
    800: '#1F2937',
    900: '#111827',
  },
};

const tintColorLight = CryptoKZColors.persianGreen;
const tintColorDark = CryptoKZColors.solar;

export const Colors = {
  light: {
    text: CryptoKZColors.black,
    background: CryptoKZColors.white,
    backgroundSecondary: CryptoKZColors.cloud,
    tint: tintColorLight,
    primary: CryptoKZColors.persianGreen,
    accent: CryptoKZColors.solar,
    icon: CryptoKZColors.gray[600],
    tabIconDefault: CryptoKZColors.gray[400],
    tabIconSelected: tintColorLight,
    border: CryptoKZColors.gray[200],
  },
  dark: {
    text: CryptoKZColors.cloud,
    background: CryptoKZColors.gray[900],
    backgroundSecondary: CryptoKZColors.gray[800],
    tint: tintColorDark,
    primary: CryptoKZColors.persianGreen,
    accent: CryptoKZColors.solar,
    icon: CryptoKZColors.gray[400],
    tabIconDefault: CryptoKZColors.gray[500],
    tabIconSelected: tintColorDark,
    border: CryptoKZColors.gray[700],
  },
};

export const Fonts = Platform.select({
  ios: {
    /** iOS `UIFontDescriptorSystemDesignDefault` */
    sans: 'system-ui',
    /** iOS `UIFontDescriptorSystemDesignSerif` */
    serif: 'ui-serif',
    /** iOS `UIFontDescriptorSystemDesignRounded` */
    rounded: 'ui-rounded',
    /** iOS `UIFontDescriptorSystemDesignMonospaced` */
    mono: 'ui-monospace',
  },
  default: {
    sans: 'normal',
    serif: 'serif',
    rounded: 'normal',
    mono: 'monospace',
  },
  web: {
    sans: "system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif",
    serif: "Georgia, 'Times New Roman', serif",
    rounded: "'SF Pro Rounded', 'Hiragino Maru Gothic ProN', Meiryo, 'MS PGothic', sans-serif",
    mono: "SFMono-Regular, Menlo, Monaco, Consolas, 'Liberation Mono', 'Courier New', monospace",
  },
});
