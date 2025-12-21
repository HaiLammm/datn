import { renderHook, act } from "@testing-library/react";
import { useFileUpload } from "./useFileUpload";

// Mock XMLHttpRequest
const mockXhr = {
  open: jest.fn(),
  send: jest.fn(),
  upload: {
    addEventListener: jest.fn(),
    removeEventListener: jest.fn(),
  },
  addEventListener: jest.fn(),
  removeEventListener: jest.fn(),
  responseText: "",
  status: 200,
  withCredentials: true,
};

// spy on the global XMLHttpRequest object
const xhrSpy = jest.spyOn(window, "XMLHttpRequest").mockImplementation(() => mockXhr as any);

describe("useFileUpload", () => {
  beforeEach(() => {
    // Reset mocks before each test
    jest.clearAllMocks();
    mockXhr.addEventListener.mockClear();
    mockXhr.upload.addEventListener.mockClear();
  });

  it("should return the initial state", () => {
    const { result } = renderHook(() => useFileUpload());

    expect(result.current.isUploading).toBe(false);
    expect(result.current.progress).toBe(0);
    expect(result.current.error).toBe(null);
    expect(result.current.isSuccess).toBe(false);
  });

  it("should reset the state", () => {
    const { result } = renderHook(() => useFileUpload());

    act(() => {
      result.current.upload({
        file: new File([""], "test.txt"),
        url: "/api/upload",
      });
    });

    act(() => {
      result.current.reset();
    });

    expect(result.current.isUploading).toBe(false);
    expect(result.current.progress).toBe(0);
    expect(result.current.error).toBe(null);
    expect(result.current.isSuccess).toBe(false);
  });

  it("should handle successful upload", async () => {
    const { result } = renderHook(() => useFileUpload());
    const onSuccess = jest.fn();
    const file = new File(["content"], "test.pdf");

    await act(async () => {
      result.current.upload({
        file,
        url: "/api/upload",
        onSuccess,
      });

      // Simulate load event
      const loadCallback = mockXhr.addEventListener.mock.calls.find(
        (call) => call[0] === "load"
      )[1];
      mockXhr.status = 200;
      mockXhr.responseText = JSON.stringify({ message: "Success" });
      loadCallback();
    });

    expect(result.current.isUploading).toBe(false);
    expect(result.current.isSuccess).toBe(true);
    expect(result.current.progress).toBe(100);
    expect(result.current.error).toBe(null);
    expect(onSuccess).toHaveBeenCalledWith({ message: "Success" });
  });

  it("should handle upload error from server", async () => {
    const { result } = renderHook(() => useFileUpload());
    const onError = jest.fn();
    const file = new File(["content"], "test.pdf");

    await act(async () => {
      result.current.upload({
        file,
        url: "/api/upload",
        onError,
      });

      // Simulate load event with error status
      const loadCallback = mockXhr.addEventListener.mock.calls.find(
        (call) => call[0] === "load"
      )[1];
      mockXhr.status = 500;
      mockXhr.responseText = JSON.stringify({ detail: "Server error" });
      loadCallback();
    });

    expect(result.current.isUploading).toBe(false);
    expect(result.current.isSuccess).toBe(false);
    expect(result.current.error).toBe("Server error");
    expect(onError).toHaveBeenCalledWith("Server error");
  });

  it("should handle network error", async () => {
    const { result } = renderHook(() => useFileUpload());
    const onError = jest.fn();

    await act(async () => {
      result.current.upload({
        file: new File([""], "test.txt"),
        url: "/api/upload",
        onError,
      });

      // Simulate error event
      const errorCallback = mockXhr.addEventListener.mock.calls.find(
        (call) => call[0] === "error"
      )[1];
      errorCallback();
    });

    expect(result.current.isUploading).toBe(false);
    expect(result.current.error).toBe("Network error. Please check your connection.");
    expect(onError).toHaveBeenCalledWith("Network error. Please check your connection.");
  });

  it("should track upload progress", async () => {
    const { result } = renderHook(() => useFileUpload());
    const onProgress = jest.fn();

    await act(async () => {
      result.current.upload({
        file: new File([""], "test.txt"),
        url: "/api/upload",
        onProgress,
      });

      // Simulate progress event
      const progressCallback = mockXhr.upload.addEventListener.mock.calls.find(
        (call) => call[0] === "progress"
      )[1];

      progressCallback({ lengthComputable: true, loaded: 50, total: 100 });
    });

    expect(result.current.progress).toBe(50);
    expect(onProgress).toHaveBeenCalledWith(50);

    // Simulate another progress event
    await act(async () => {
      const progressCallback = mockXhr.upload.addEventListener.mock.calls.find(
        (call) => call[0] === "progress"
      )[1];
      progressCallback({ lengthComputable: true, loaded: 100, total: 100 });
    });

    expect(result.current.progress).toBe(100);
    expect(onProgress).toHaveBeenCalledWith(100);
  });
});
