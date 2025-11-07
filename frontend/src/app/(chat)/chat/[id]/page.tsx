import { Chat } from "@/components/ai/chat";
import { getChatMessages } from "@/lib/api/ai";
import type { UIMessage } from "ai";

interface ChatPageProps {
  params: Promise<{ id: string }>;
}

export default async function ChatPage({ params }: ChatPageProps) {
  const { id } = await params;
  const data = await getChatMessages(id);

  return (
    <div className="flex flex-1 justify-center overflow-y-auto px-4 pb-20 md:px-10">
      <Chat id={id} initialMessages={data.messages as UIMessage[]} />
    </div>
  );
}
