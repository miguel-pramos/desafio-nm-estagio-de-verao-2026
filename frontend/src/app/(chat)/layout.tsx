import { getUser } from "@/lib/api/auth";
import { redirect } from "next/navigation";
import { UserProvider } from "@/contexts/user-context";

export default async function ChatLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const user = await getUser();

  if (!user) {
    redirect("/sign-in");
  }

  return <UserProvider user={user}>{children}</UserProvider>;
}
