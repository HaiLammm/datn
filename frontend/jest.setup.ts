import '@testing-library/jest-dom';

// Mock window.alert as it's not implemented in JSDOM
window.alert = jest.fn();

// Mock ResizeObserver for Radix UI components
class ResizeObserverMock {
  observe() {}
  unobserve() {}
  disconnect() {}
}
global.ResizeObserver = ResizeObserverMock;

// Mock PointerEvent for Radix UI
class PointerEventMock extends MouseEvent {
  constructor(type: string, props: PointerEventInit = {}) {
    super(type, props);
  }
}
global.PointerEvent = PointerEventMock as typeof PointerEvent;

// Mock Element.prototype methods for Radix UI
if (typeof Element.prototype.hasPointerCapture === 'undefined') {
  Element.prototype.hasPointerCapture = () => false;
}
if (typeof Element.prototype.setPointerCapture === 'undefined') {
  Element.prototype.setPointerCapture = () => {};
}
if (typeof Element.prototype.releasePointerCapture === 'undefined') {
  Element.prototype.releasePointerCapture = () => {};
}

// Mock scrollIntoView
Element.prototype.scrollIntoView = jest.fn();