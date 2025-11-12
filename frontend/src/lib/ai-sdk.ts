import { DefaultChatTransport } from "ai";
import { getApiBaseUrl, joinApi } from "@/lib/url";

export function createFastapiChatTransport() {
  return new DefaultChatTransport({
    api: joinApi(getApiBaseUrl(), "/chat"),
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
