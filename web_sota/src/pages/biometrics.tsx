import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Lock, UserCheck, ShieldCheck, Activity } from "lucide-react";

export function Biometrics() {
    return (
        <div className="space-y-6">
            <div className="flex flex-col gap-2">
                <h1 className="text-3xl font-bold tracking-tight text-white">Biometric Security</h1>
                <p className="text-slate-400 italic">Face-recognition gatekeeper and intrusion detection telemetry.</p>
            </div>

            <div className="grid gap-4 md:grid-cols-2">
                <Card className="border-slate-800 bg-slate-950/50 overflow-hidden">
                    <CardHeader className="border-b border-slate-800">
                        <CardTitle className="text-slate-200 flex items-center gap-2">
                            <Activity className="h-4 w-4 text-emerald-500" />
                            Live Detection
                        </CardTitle>
                    </CardHeader>
                    <CardContent className="h-[300px] flex items-center justify-center bg-slate-900/50 relative">
                        <div className="absolute inset-0 border-2 border-emerald-500/20 animate-pulse m-10 rounded-xl" />
                        <UserCheck className="h-24 w-24 text-emerald-500 opacity-50" />
                        <div className="absolute bottom-4 left-4 text-xs font-mono text-emerald-500 bg-black/50 p-2 rounded">
                            MATCH: Sandra Schipal [98.4%]
                        </div>
                    </CardContent>
                </Card>

                <Card className="border-slate-800 bg-slate-950/50">
                    <CardHeader>
                        <CardTitle className="text-slate-200 flex items-center gap-2">
                            <ShieldCheck className="h-4 w-4 text-blue-500" />
                            Security Protocols
                        </CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-4">
                        <div className="flex justify-between p-4 border border-slate-800 rounded-lg bg-emerald-500/5">
                            <div className="flex items-center gap-3">
                                <Lock className="h-5 w-5 text-emerald-500" />
                                <span className="text-sm font-medium text-slate-200">System Lock Status</span>
                            </div>
                            <span className="text-emerald-500 font-bold">SECURED</span>
                        </div>
                        <div className="p-4 border border-slate-800 rounded-lg space-y-2">
                            <span className="text-xs text-slate-500 uppercase tracking-widest">Authorized Personas</span>
                            <div className="flex flex-wrap gap-2 pt-2">
                                <span className="px-3 py-1 bg-slate-800 rounded-full text-xs text-slate-300">Sandra Schipal</span>
                                <span className="px-3 py-1 bg-slate-800 rounded-full text-xs text-slate-300">Steve [MOCK]</span>
                            </div>
                        </div>
                    </CardContent>
                </Card>
            </div>
        </div>
    );
}
