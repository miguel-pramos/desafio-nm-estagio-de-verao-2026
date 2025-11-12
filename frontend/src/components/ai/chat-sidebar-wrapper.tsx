"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { toast } from "sonner";
import { ChatSidebar, type ChatSummary } from "@/components/ai/chat-sidebar";

interface ChatSidebarWrapperProps {
  chats: ChatSummary[];
  activeChatId?: string;
}

export function ChatSidebarWrapper({
  chats: initialChats,
  activeChatId,
}: ChatSidebarWrapperProps) {
  const router = useRouter();
  const [chats, setChats] = useState(initialChats);

  const handleDeleteChat = async (chatId: string) => {
    try {
      const response = await fetch(`/api/chat/${chatId}`, {
        method: "DELETE",
      });

      if (!response.ok) {
        throw new Error("Failed to delete chat");
      }

      // Remove the chat from the local state
      setChats((prevChats) => prevChats.filter((chat) => chat.id !== chatId));

      toast.success("Conversa deletada com sucesso");

      // If the deleted chat is the active one, redirect to home
      if (chatId === activeChatId) {
        router.push("/");
      }
    } catch (error) {
      console.error("Failed to delete chat:", error);
      toast.error("Erro ao deletar conversa");
    }
  };

  return (
    <ChatSidebar
      chats={chats}
      activeChatId={activeChatId}
      onDeleteChat={handleDeleteChat}
    />
  );
}

export type { ChatSummary } from "./chat-sidebar";
