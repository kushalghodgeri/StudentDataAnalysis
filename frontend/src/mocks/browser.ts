import { setupWorker } from "msw/browser";
import { handlers } from "./handlers";

export const worker = setupWorker(...handlers);

export async function enableMocking(): Promise<void> {
  const useMocks = import.meta.env.VITE_USE_MOCKS === "true";
  if (!useMocks) {
    return;
  }

  // Start MSW service worker in the browser
  await worker.start({
    onUnhandledRequest: "bypass",
  });
  console.log("Mock Service Worker (MSW) enabled for API calls.");
}
