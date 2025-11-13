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
import {
  ChatSidebarWrapper,
  type ChatSummary,
} from "@/components/ai/chat-sidebar-wrapper";
import { getUserChats } from "@/lib/api/ai";
import { getUser } from "@/lib/api/auth";

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
  // Check if user is authenticated before fetching chats
  const user = await getUser();
  let chats: ChatSummary[] = [];

  // Only fetch chats for authenticated users (not on sign-in page)
  if (user) {
    try {
      const listResp = await getUserChats();
      chats = (listResp?.chats ?? []).map((c) => ({
        id: c.id,
        title: c.title ?? undefined,
        preview: c.preview ?? undefined,
        lastRole: c.lastRole ?? undefined,
        // Ensure updatedAt is a string (the sidebar expects ISO string)
        updatedAt:
          c.updatedAt instanceof Date
            ? c.updatedAt.toISOString()
            : String(c.updatedAt),
      }));
    } catch (error) {
      // If fetching chats fails, continue with empty chats
      console.error("Failed to fetch chats:", error);
      chats = [];
    }
  }

  return (
    <html lang="pt-BR" className={`${geist.variable}`}>
      <body>
        <App>
          <SidebarProvider
            style={
              {
                "--sidebar-width": "20rem",
                "--sidebar-width-mobile": "20rem",
              } as React.CSSProperties
            }
          >
            <ChatSidebarWrapper chats={chats}/>
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
