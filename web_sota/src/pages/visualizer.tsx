import { Card, CardContent } from "@/components/ui/card";
import { Video, Maximize } from "lucide-react";

export function Visualizer() {
    return (
        <div className="space-y-6">
            <div className="flex items-center justify-between">
                <div>
                    <h2 className="text-2xl font-bold tracking-tight text-white">3D Visualizer</h2>
                    <p className="text-slate-400">Digital twin and environment mapping</p>
                </div>
            </div>

            <Card className="border-slate-800 bg-slate-950/50 overflow-hidden">
                <CardContent className="p-0 aspect-[16/9] relative bg-slate-900 flex items-center justify-center">
                    {/* Placeholder for Three.js / Unity WebGL View */}
                    <div className="text-center space-y-4">
                        <div className="inline-flex h-16 w-16 items-center justify-center rounded-full bg-slate-800/50">
                            <Video className="h-8 w-8 text-slate-500" />
                        </div>
                        <div>
                            <h3 className="text-lg font-medium text-slate-300">Unity Bridge Disconnected</h3>
                            <p className="text-sm text-slate-500">Start the Unity simulation to view 3D telemetry</p>
                        </div>
                    </div>

                    <div className="absolute bottom-4 right-4">
                        <button className="p-2 bg-black/50 hover:bg-black/70 rounded text-white transition-colors">
                            <Maximize className="h-5 w-5" />
                        </button>
                    </div>
                </CardContent>
            </Card>
        </div>
    );
}
