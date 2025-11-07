import "@/styles/globals.css";

import {
  App,
  AppHeader,
  AppHeaderActions,
  AppHeaderTitle,
  AppMain,
} from "@/components/app";
import { AuthSection } from "@/components/auth/AuthSection";
import { type Metadata, type Viewport } from "next";
import { Geist } from "next/font/google";
import Link from "next/link";
import { SidebarInset, SidebarProvider } from "@/components/ui/sidebar";
import { ChatSidebar } from "@/components/ai/chat-sidebar";
import { getUserChats } from "@/lib/api/ai";

export const metadata: Metadata = {
  title: "Unicamp VestIA",
  description: "Chat IA para tirar dúvidas sobre o Vestibular Unicamp 2026.",
  icons: [{ rel: "icon", url: "/favicon.ico" }],
};

export const viewport: Viewport = {
  width: "device-width",
  initialScale: 1,
  maximumScale: 1,
  userScalable: false,
};

const geist = Geist({
  subsets: ["latin"],
  variable: "--font-geist-sans",
});

export default async function RootLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  const listResp = await getUserChats();

  const chats: ChatSummary[] = (listResp?.chats ?? []).map((c) => ({
    id: c.id,
    preview: c.preview ?? undefined,
    lastRole: (c as any).lastRole ?? undefined,
    // Ensure updatedAt is a string (the sidebar expects ISO string)
    updatedAt:
      c.updatedAt instanceof Date
        ? c.updatedAt.toISOString()
        : String(c.updatedAt),
  }));

  return (
    <html lang="pt-BR" className={`${geist.variable}`}>
      <body>
        <App>
          <SidebarProvider>
            <ChatSidebar chats={chats} />
            <SidebarInset className="bg-background">
              <AppHeader>
                <AppHeaderTitle asChild>
                  <Link href="/">Unicamp VestIA</Link>
                </AppHeaderTitle>

                <AppHeaderActions>
                  <AuthSection />
                </AppHeaderActions>
              </AppHeader>

              <AppMain>{children}</AppMain>
            </SidebarInset>
          </SidebarProvider>
        </App>
      </body>
    </html>
  );
}
