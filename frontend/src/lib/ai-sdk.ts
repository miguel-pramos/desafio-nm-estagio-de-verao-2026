import { DefaultChatTransport } from "ai";

export function createFastapiChatTransport() {
  return new DefaultChatTransport({
    // Use Next.js API route as a proxy to avoid cross-origin cookie issues
    api: "/api/chat",
    credentials: "include",
    // Only send the last message to the server
    prepareSendMessagesRequest({ messages, id }) {
      return {
        body: {
          message: messages[messages.length - 1],
          id,
        },
      };
    },
  });
}
