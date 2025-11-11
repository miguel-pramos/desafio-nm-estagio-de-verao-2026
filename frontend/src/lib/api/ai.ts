import { chatApi } from "@/lib/fastapi-client";
import type { ReadonlyHeaders } from "next/dist/server/web/spec-extension/adapters/headers";
import { headers } from "next/headers";

export async function createChat() {
  const headersList = await headers();
  console.log("createChat: ",headersList);

  return chatApi.createNewChatChatCreatePost({
    headers: headersList,
  });
}

export async function getChatMessages(chatId: string) {
  const headersList: ReadonlyHeaders = await headers();
  console.log("getChatMessages: ",headersList);

  return chatApi.getChatMessagesChatChatIdGet(
    { chatId },
    {
      headers: headersList,
      cache: "no-store",
    },
  );
}

export async function getUserChats(limit?: number) {
  const headersList = await headers();
  console.log("getUserChats: ", headersList);

  return chatApi.getUserChatsChatGet(
    { limit },
    {
      headers: headersList,
      cache: "no-store",
    },
  );
}
