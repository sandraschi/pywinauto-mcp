import { useEffect, useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Activity, GitMerge, Box, LayoutDashboard } from "lucide-react";
import { apiPath } from "@/lib/api";

export function Dashboard() {
    const [bridge, setBridge] = useState<"loading" | "ok" | "error">("loading");
    const [bridgeDetail, setBridgeDetail] = useState<string>("");

    useEffect(() => {
        let cancelled = false;
        fetch(apiPath("/api/v1/health"))
            .then(async (r) => {
                const j = await r.json().catch(() => ({}));
                if (cancelled) return;
                if (r.ok && (j as { status?: string }).status === "ok") {
                    setBridge("ok");
                    setBridgeDetail("REST bridge reachable");
                } else {
                    setBridge("error");
                    setBridgeDetail(`HTTP ${r.status}`);
                }
            })
            .catch((e) => {
                if (!cancelled) {
                    setBridge("error");
                    setBridgeDetail(String(e));
                }
            });
        return () => {
            cancelled = true;
        };
    }, []);

    return (
        <div className="space-y-6">
            <div className="flex flex-wrap items-center justify-between gap-3">
                <div>
                    <h2 className="text-2xl font-bold tracking-tight text-white">Automation Dashboard</h2>
                    <p className="text-slate-400">
                        [MOCK] Demo metrics below — not live MCP telemetry. Backend:{" "}
                        {bridge === "loading" && <span className="text-slate-500">checking…</span>}
                        {bridge === "ok" && (
                            <Badge variant="outline" className="border-emerald-500/40 text-emerald-400">
                                connected — {bridgeDetail}
                            </Badge>
                        )}
                        {bridge === "error" && (
                            <Badge variant="outline" className="border-amber-500/40 text-amber-400">
                                unreachable — {bridgeDetail}
                            </Badge>
                        )}
                    </p>
                </div>
                <Badge variant="secondary" className="bg-slate-800 text-slate-300">
                    [MOCK] UI preview
                </Badge>
            </div>

            {/* KPI Cards */}
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
                <Card className="border-slate-800 bg-slate-950/50">
                    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                        <CardTitle className="text-sm font-medium text-slate-200">
                            Active Windows
                        </CardTitle>
                        <LayoutDashboard className="h-4 w-4 text-emerald-500" />
                    </CardHeader>
                    <CardContent>
                        <div className="text-2xl font-bold text-white">
                            <span className="text-slate-500 text-sm font-normal mr-2">[MOCK]</span>42
                        </div>
                        <p className="text-xs text-slate-400">[MOCK] +5 from last scan (placeholder)</p>
                    </CardContent>
                </Card>

                <Card className="border-slate-800 bg-slate-950/50">
                    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                        <CardTitle className="text-sm font-medium text-slate-200">
                            Automation State
                        </CardTitle>
                        <Activity className="h-4 w-4 text-blue-500" />
                    </CardHeader>
                    <CardContent>
                        <div className="text-2xl font-bold text-white">
                            <span className="text-slate-500 text-sm font-normal mr-2">[MOCK]</span>—
                        </div>
                        <p className="text-xs text-slate-400">[MOCK] Not wired to server runtime state</p>
                    </CardContent>
                </Card>

                <Card className="border-slate-800 bg-slate-950/50">
                    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                        <CardTitle className="text-sm font-medium text-slate-200">
                            OCR / Vision
                        </CardTitle>
                        <Box className="h-4 w-4 text-purple-500" />
                    </CardHeader>
                    <CardContent>
                        <div className="text-2xl font-bold text-white">—</div>
                        <p className="text-xs text-slate-400">OCR uses Tesseract when installed on host</p>
                    </CardContent>
                </Card>

                <Card className="border-slate-800 bg-slate-950/50">
                    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                        <CardTitle className="text-sm font-medium text-slate-200">
                            Face Security
                        </CardTitle>
                        <GitMerge className="h-4 w-4 text-orange-500" />
                    </CardHeader>
                    <CardContent>
                        <div className="text-2xl font-bold text-white">
                            <span className="text-slate-500 text-sm font-normal mr-2">[MOCK]</span>—
                        </div>
                        <p className="text-xs text-slate-400">[MOCK] Face tools opt-in via env (see Help)</p>
                    </CardContent>
                </Card>
            </div>

            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-7">
                <Card className="col-span-4 border-slate-800 bg-slate-950/50">
                    <CardHeader>
                        <CardTitle className="text-white">Recent Telemetry</CardTitle>
                    </CardHeader>
                    <CardContent>
                        <div className="h-[200px] flex items-center justify-center border border-dashed border-slate-800 rounded-md bg-slate-900/20">
                            <span className="text-slate-500 text-sm">[MOCK] Real-time telemetry graph placeholder</span>
                        </div>
                    </CardContent>
                </Card>
                <Card className="col-span-3 border-slate-800 bg-slate-950/50">
                    <CardHeader>
                        <CardTitle className="text-white">Recent Automation Log</CardTitle>
                    </CardHeader>
                    <CardContent>
                        <div className="space-y-4">
                            <div className="flex items-center">
                                <span className="relative flex h-2 w-2 mr-2">
                                    <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                                    <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
                                </span>
                                <div className="ml-2 space-y-1">
                                    <p className="text-sm font-medium leading-none text-white">Window Health Check</p>
                                    <p className="text-xs text-slate-400">Status: All windows responsive</p>
                                </div>
                                <div className="ml-auto font-mono text-xs text-slate-400">23:25:43</div>
                            </div>
                            <div className="flex items-center">
                                <span className="relative flex h-2 w-2 mr-2 bg-slate-700 rounded-full"></span>
                                <div className="ml-2 space-y-1">
                                    <p className="text-sm font-medium leading-none text-white text-opacity-50">
                                        <span className="text-slate-500 text-xs mr-1">[MOCK]</span>Face Template Update
                                    </p>
                                    <p className="text-xs text-slate-500">[MOCK] Security Module • Queued</p>
                                </div>
                            </div>
                        </div>
                    </CardContent>
                </Card>
            </div>
        </div>
    );
}
