import { useEffect, useState } from "react";
import { getApiBaseUrl } from "@/utils/storage";

type ApiStatus = "checking" | "online" | "offline" | "suspended";

export function ApiStatusBanner() {
  const [status, setStatus] = useState<ApiStatus>("checking");

  useEffect(() => {
    const check = async () => {
      try {
        const res = await fetch(`${getApiBaseUrl()}/api/v1/health`, {
          method: "GET",
        });
        if (res.status === 503) {
          setStatus("suspended");
          return;
        }
        setStatus(res.ok ? "online" : "offline");
      } catch {
        setStatus("offline");
      }
    };
    void check();
  }, []);

  if (status === "checking" || status === "online") {
    return null;
  }

  return (
    <div className="rounded-xl border border-amber-500/30 bg-amber-500/10 px-4 py-3 text-sm text-amber-700 dark:text-amber-300 space-y-1">
      {status === "suspended" ? (
        <>
          <p className="font-medium">
            API 서버가 중지(Suspended)되어 Vercel 로그인이 불가능합니다
          </p>
          <p className="text-xs opacity-90">
            기존 <strong>growthpilot-api</strong> 는 Resume 이 안 되는 경우가 많습니다.
            Render에서 <strong>새 Web Service</strong>(예: ai-tutor-api)를 만든 뒤 Vercel
            환경 변수 <code className="text-[11px]">VITE_API_BASE_URL</code> 을 새 URL로
            바꾸고 Redeploy 하세요. 새 DB이므로 <strong>회원가입</strong>이 필요합니다.
          </p>
          <p className="text-xs opacity-90">
            지금 바로 쓰려면 로컬:{" "}
            <a href="http://127.0.0.1:5173" className="underline">
              http://127.0.0.1:5173
            </a>{" "}
            (백엔드·프론트 실행 후 회원가입)
          </p>
        </>
      ) : (
        <>
          <p className="font-medium">API 서버에 연결할 수 없습니다</p>
          <p className="text-xs opacity-90">
            로컬 사용 시 백엔드(<code className="text-[11px]">uvicorn</code>)와
            프론트(<code className="text-[11px]">npm run dev</code>)가 실행 중인지
            확인하세요.
          </p>
        </>
      )}
    </div>
  );
}
