import { chatApi } from "@/lib/fastapi-client";
import { headers } from "next/headers";
import { object } from "zod/v4";

export async function createChat() {
  const headersList = new Headers(await headers());
  console.log(headersList)

  return chatApi.createNewChatChatCreatePost({
    headers: headersList,
  });
}

export async function getChatMessages(chatId: string) {
  const headersList = Object.fromEntries(await headers());
  console.log(headersList)
  return chatApi.getChatMessagesChatChatIdGet(
    { chatId },
    {
      headers: headersList,
      cache: "no-store",
    },
  );
}

export async function getUserChats(limit?: number) {
  const headersList = Object.fromEntries(await headers());
  console.log(headersList)

  return chatApi.getUserChatsChatGet(
    { limit },
    {
      headers: headersList,
      cache: "no-store",
    },
  );
}
