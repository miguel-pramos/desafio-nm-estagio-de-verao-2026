import { Button } from "@/components/ui/button";
import Link from "next/link";
import { getApiBaseUrl, joinApi } from "@/lib/url";

function LoginButton() {
  return (
    <Button asChild>
      <Link href={joinApi(getApiBaseUrl(), "/auth/github/login")}>
        Entrar com GitHub
      </Link>
    </Button>
  );
}

export { LoginButton };
