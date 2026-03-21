import { useEffect, useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Lock, UserCheck, ShieldCheck, Activity } from "lucide-react";
import { CameraSelect } from "@/components/CameraSelect";
import { readStoredCameraIndex, useCameras, writeStoredCameraIndex } from "@/hooks/useCameras";

export function Biometrics() {
    const { cameras, loading, error, refresh } = useCameras();
    const [cameraIndex, setCameraIndex] = useState(0);

    useEffect(() => {
        if (cameras.length === 0) return;
        const stored = readStoredCameraIndex();
        const pick =
            stored !== null && cameras.some((c) => c.index === stored) ? stored : cameras[0].index;
        setCameraIndex(pick);
    }, [cameras]);

    const handleCameraChange = (index: number) => {
        setCameraIndex(index);
        writeStoredCameraIndex(index);
    };

    return (
        <div className="space-y-6">
            <div className="flex flex-col gap-2">
                <h1 className="text-3xl font-bold tracking-tight text-white">Biometric Security</h1>
                <p className="text-slate-400">
                    Face capture uses OpenCV on the host. Select a camera when multiple devices are available; the same
                    choice syncs to the Tools hub for <code className="text-slate-500">automation_face</code> (
                    <code className="text-slate-500">camera_index</code>).
                </p>
            </div>

            <Card className="border-slate-800 bg-slate-950/50">
                <CardHeader className="border-b border-slate-800">
                    <CardTitle className="text-slate-200 flex items-center gap-2 text-base">
                        <Activity className="h-4 w-4 text-cyan-500" />
                        Camera device
                    </CardTitle>
                </CardHeader>
                <CardContent className="pt-6">
                    <CameraSelect
                        cameras={cameras}
                        loading={loading}
                        error={error}
                        onRefresh={() => void refresh()}
                        value={cameraIndex}
                        onChange={handleCameraChange}
                        id="biometrics-camera"
                        label="Capture device"
                    />
                    <p className="text-xs text-slate-500 mt-3">
                        Index <code className="text-slate-400">{cameraIndex}</code> is passed to face capture when you run
                        tools from the MCP server. See <code className="text-slate-400">docs/SAFETY.md</code> §5.
                    </p>
                </CardContent>
            </Card>

            <div className="grid gap-4 md:grid-cols-2">
                <Card className="border-slate-800 bg-slate-950/50 overflow-hidden">
                    <CardHeader className="border-b border-slate-800 flex flex-row items-center justify-between">
                        <CardTitle className="text-slate-200 flex items-center gap-2">
                            <Activity className="h-4 w-4 text-emerald-500" />
                            Live Detection
                        </CardTitle>
                        <Badge variant="secondary" className="bg-amber-950/50 text-amber-400 border-amber-800/50">
                            [MOCK]
                        </Badge>
                    </CardHeader>
                    <CardContent className="h-[300px] flex items-center justify-center bg-slate-900/50 relative">
                        <div className="absolute inset-0 border-2 border-emerald-500/20 animate-pulse m-10 rounded-xl" />
                        <UserCheck className="h-24 w-24 text-emerald-500 opacity-50" />
                        <div className="absolute bottom-4 left-4 text-xs font-mono text-emerald-500 bg-black/50 p-2 rounded">
                            [MOCK] MATCH: placeholder [0%]
                        </div>
                    </CardContent>
                </Card>

                <Card className="border-slate-800 bg-slate-950/50">
                    <CardHeader className="flex flex-row items-center justify-between">
                        <CardTitle className="text-slate-200 flex items-center gap-2">
                            <ShieldCheck className="h-4 w-4 text-blue-500" />
                            Security Protocols
                        </CardTitle>
                        <Badge variant="secondary" className="bg-amber-950/50 text-amber-400 border-amber-800/50">
                            [MOCK]
                        </Badge>
                    </CardHeader>
                    <CardContent className="space-y-4">
                        <div className="flex justify-between p-4 border border-slate-800 rounded-lg bg-emerald-500/5">
                            <div className="flex items-center gap-3">
                                <Lock className="h-5 w-5 text-emerald-500" />
                                <span className="text-sm font-medium text-slate-200">System Lock Status</span>
                            </div>
                            <span className="text-emerald-500 font-bold">[MOCK] SECURED</span>
                        </div>
                        <div className="p-4 border border-slate-800 rounded-lg space-y-2">
                            <span className="text-xs text-slate-500 uppercase tracking-widest">
                                [MOCK] Authorized Personas
                            </span>
                            <div className="flex flex-wrap gap-2 pt-2">
                                <span className="px-3 py-1 bg-slate-800 rounded-full text-xs text-slate-500">
                                    Configure via server / known_faces
                                </span>
                            </div>
                        </div>
                    </CardContent>
                </Card>
            </div>
        </div>
    );
}
