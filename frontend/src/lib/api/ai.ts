import { chatApi } from "@/lib/fastapi-client";
import { headers } from "next/headers";

export async function createChat() {
  const headersList = new Headers(await headers());
  return chatApi.createNewChatChatCreatePost({
    headers: headersList,
  });
}

export async function getChatMessages(chatId: string) {
  const headersList = new Headers(await headers());
  return chatApi.getChatMessagesChatChatIdGet(
    { chatId },
    {
      headers: headersList,
      cache: "no-store",
    },
  );
}

export async function getUserChats(limit?: number) {
  const headersList = new Headers(await headers());
  return chatApi.getUserChatsChatGet(
    { limit },
    {
      headers: headersList,
      cache: "no-store",
    },
  );
}
