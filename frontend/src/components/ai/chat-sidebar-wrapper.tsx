"use client";

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

  const handleDeleteChat = async (chatId: string) => {
    try {
      const response = await fetch(`/api/chat/${chatId}`, {
        method: "DELETE",
      });

      if (!response.ok) {
        throw new Error("Failed to delete chat");
      }

      toast.success("Conversa deletada com sucesso");

      // If the deleted chat is the active one, redirect to home
      if (chatId === activeChatId) {
        router.push("/");
      } else {
        // Refresh the page to update the chat list
        window.location.reload();
      }
    } catch (error) {
      console.error("Failed to delete chat:", error);
      toast.error("Erro ao deletar conversa");
    }
  };

  return (
    <ChatSidebar
      chats={initialChats}
      activeChatId={activeChatId}
      onDeleteChat={handleDeleteChat}
    />
  );
}

export type { ChatSummary } from "./chat-sidebar";
