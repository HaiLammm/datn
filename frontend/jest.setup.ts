import '@testing-library/jest-dom';

// Mock window.alert as it's not implemented in JSDOM
window.alert = jest.fn();