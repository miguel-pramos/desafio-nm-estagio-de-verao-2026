"use client";

import Link from "next/link";
import { MessageSquare, Plus, Trash2 } from "lucide-react";

import {
  Sidebar,
  SidebarContent,
  SidebarGroup,
  SidebarGroupContent,
  SidebarGroupLabel,
  SidebarHeader,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
  SidebarSeparator,
  SidebarTrigger,
} from "@/components/ui/sidebar";

type ChatSummary = {
  id: string;
  preview?: string;
  lastRole?: string | null;
  updatedAt: string;
};

interface ChatSidebarProps {
  chats: ChatSummary[];
  activeChatId?: string;
  onDeleteChat?: (chatId: string) => void;
}

function ChatSidebar({ chats, activeChatId, onDeleteChat }: ChatSidebarProps) {
  return (
    <Sidebar
      collapsible="icon"
      className="border-sidebar-border border-r"
      variant="sidebar"
    >
      <SidebarHeader className="border-sidebar-border border-b py-3">
        <div className="flex items-center justify-between gap-2">
          <SidebarTrigger size={"lg"} className="ml-auto" />
        </div>
      </SidebarHeader>

      <SidebarContent>
        <SidebarGroup>
          <SidebarGroupLabel>Conversas</SidebarGroupLabel>
          <SidebarGroupContent>
            <SidebarMenu>
              <SidebarMenuItem>
                <SidebarMenuButton asChild tooltip="Nova conversa" size="lg">
                  <Link href="/" className="flex w-full items-center gap-3">
                    <span className="border-sidebar-border text-sidebar-foreground flex size-8 items-center justify-center rounded-md border border-dashed">
                      <Plus className="size-4" />
                    </span>
                    <span className="group-data-[collapsible=icon]:hidden">
                      Nova conversa
                    </span>
                  </Link>
                </SidebarMenuButton>
              </SidebarMenuItem>

              <SidebarSeparator />

              {chats.length === 0 ? (
                <SidebarMenuItem>
                  <SidebarMenuButton
                    disabled
                    size="lg"
                    className="cursor-default"
                    tooltip="Sem conversas no momento"
                  >
                    <span className="bg-muted text-muted-foreground flex size-8 items-center justify-center rounded-md">
                      <MessageSquare className="size-4" />
                    </span>
                    <span className="group-data-[collapsible=icon]:hidden">
                      Nenhuma conversa ainda
                    </span>
                  </SidebarMenuButton>
                </SidebarMenuItem>
              ) : (
                chats.map((chat, index) => {
                  const title = buildChatTitle(chat.preview, index);
                  const relativeTime = formatRelativeTime(chat.updatedAt);

                  return (
                    <SidebarMenuItem key={chat.id} className="group">
                      <div className="flex items-center gap-2">
                        <SidebarMenuButton
                          asChild
                          size="lg"
                          tooltip={title}
                          isActive={chat.id === activeChatId}
                          className="flex-1"
                        >
                          <Link
                            href={`/chat/${chat.id}`}
                            className="flex w-full items-center gap-3"
                          >
                            <span className="bg-sidebar-accent text-sidebar-accent-foreground flex size-8 items-center justify-center rounded-md">
                              <MessageSquare className="size-4" />
                            </span>
                            <span className="min-w-0 flex-1 group-data-[collapsible=icon]:hidden">
                              <span className="text-sidebar-foreground block truncate text-sm leading-tight font-medium">
                                {title}
                              </span>
                            </span>
                            {relativeTime && (
                              <span className="text-sidebar-foreground/60 ml-auto shrink-0 text-[10px] tracking-wide uppercase group-data-[collapsible=icon]:hidden">
                                {relativeTime}
                              </span>
                            )}
                          </Link>
                        </SidebarMenuButton>
                        {onDeleteChat && (
                          <button
                            onClick={(e) => {
                              e.preventDefault();
                              e.stopPropagation();
                              onDeleteChat(chat.id);
                            }}
                            className="text-sidebar-foreground/60 hover:text-sidebar-foreground group-hover:flex size-8 items-center justify-center rounded-md hidden "
                            title="Deletar conversa"
                          >
                            <Trash2 className="size-4" />
                          </button>
                        )}
                      </div>
                    </SidebarMenuItem>
                  );
                })
              )}
            </SidebarMenu>
          </SidebarGroupContent>
        </SidebarGroup>
      </SidebarContent>
    </Sidebar>
  );
}

function buildChatTitle(preview: string | undefined, index: number) {
  const base = preview?.trim();
  if (base) {
    const firstLine = base.split(/\n+/)[0] ?? base;
    return firstLine.slice(0, 48);
  }
  return `Conversa ${index + 1}`;
}

function formatRelativeTime(value: string) {
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) {
    return "";
  }

  const diffMs = date.getTime() - Date.now();
  const diffMinutes = Math.round(diffMs / 60000);

  if (Math.abs(diffMinutes) < 1) {
    return "agora";
  }

  const absMinutes = Math.abs(diffMinutes);
  let amount: number;
  let unit: string;

  if (absMinutes < 60) {
    amount = absMinutes;
    unit = "m";
  } else if (absMinutes < 60 * 24) {
    amount = Math.round(absMinutes / 60);
    unit = "h";
  } else if (absMinutes < 60 * 24 * 7) {
    amount = Math.round(absMinutes / (60 * 24));
    unit = "d";
  } else if (absMinutes < 60 * 24 * 30) {
    amount = Math.round(absMinutes / (60 * 24 * 7));
    unit = "sem";
  } else if (absMinutes < 60 * 24 * 365) {
    amount = Math.round(absMinutes / (60 * 24 * 30));
    unit = "mes";
  } else {
    amount = Math.round(absMinutes / (60 * 24 * 365));
    unit = "a";
  }

  return diffMinutes < 0 ? `há ${amount}${unit}` : `em ${amount}${unit}`;
}

export { ChatSidebar };
export type { ChatSidebarProps, ChatSummary };
