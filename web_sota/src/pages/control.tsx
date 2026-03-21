import {
    Card,
    CardContent,
    CardHeader,
    CardTitle,
} from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import {
    Battery,
    Wifi,
    Power,
    Play,
    Square,
    RefreshCw,
    Video,
    Activity,
    Zap
} from "lucide-react";

// Mock Data from legacy temp_robot_control.tsx
interface RobotStatus {
    id: string;
    name: string;
    type: 'humanoid' | 'quadruped' | 'wheeled';
    status: 'online' | 'offline' | 'error' | 'charging';
    battery: number;
    wifi: number;
    temperature: number;
    task: string;
}

const ROBOTS: RobotStatus[] = [
    {
        id: 'unitree-h1',
        name: 'Unitree H1',
        type: 'humanoid',
        status: 'online',
        battery: 87,
        wifi: 92,
        temperature: 45,
        task: 'Idle - Ready for teleop'
    },
    {
        id: 'go2-alpha',
        name: 'Go2 Alpha',
        type: 'quadruped',
        status: 'charging',
        battery: 45,
        wifi: 88,
        temperature: 38,
        task: 'Charging - Dock A'
    },
    {
        id: 'scout-mini',
        name: 'Scout Mini',
        type: 'wheeled',
        status: 'offline',
        battery: 0,
        wifi: 0,
        temperature: 0,
        task: 'Connection lost'
    }
];

export function Control() {
    return (
        <div className="space-y-6">
            <div className="flex items-center justify-between">
                <div>
                    <h2 className="text-2xl font-bold tracking-tight text-white">Control Center</h2>
                    <p className="text-slate-400">Direct teleoperation and fleet management</p>
                </div>
                <div className="flex gap-2">
                    <Button variant="outline" className="border-slate-800 bg-slate-900/50 hover:bg-slate-800">
                        <RefreshCw className="mr-2 h-4 w-4" />
                        Refresh
                    </Button>
                    <Button className="bg-emerald-600 hover:bg-emerald-700 text-white border-0">
                        <Power className="mr-2 h-4 w-4" />
                        Emergency Stop
                    </Button>
                </div>
            </div>

            <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
                {ROBOTS.map((robot) => (
                    <RobotCard key={robot.id} robot={robot} />
                ))}
            </div>

            <Tabs defaultValue="teleop" className="space-y-4">
                <TabsList className="bg-slate-900/50 border border-slate-800">
                    <TabsTrigger value="teleop" className="data-[state=active]:bg-slate-800">Teleoperation</TabsTrigger>
                    <TabsTrigger value="logs" className="data-[state=active]:bg-slate-800">System Logs</TabsTrigger>
                    <TabsTrigger value="config" className="data-[state=active]:bg-slate-800">Configuration</TabsTrigger>
                </TabsList>
                <TabsContent value="teleop" className="space-y-4">
                    <TeleopPanel />
                </TabsContent>
                <TabsContent value="logs">
                    <Card className="border-slate-800 bg-slate-950/50">
                        <CardHeader>
                            <CardTitle>System Events</CardTitle>
                        </CardHeader>
                        <CardContent>
                            <div className="font-mono text-sm text-slate-400 space-y-2">
                                <p>[10:42:15] <span className="text-emerald-500">INFO</span> Unitree H1 connected to control server</p>
                                <p>[10:41:22] <span className="text-yellow-500">WARN</span> Go2 Alpha latency spike (145ms)</p>
                                <p>[10:40:05] <span className="text-blue-500">DEBUG</span> Mqtt connection established on wss://robotics.local</p>
                            </div>
                        </CardContent>
                    </Card>
                </TabsContent>
            </Tabs>
        </div>
    );
}

function RobotCard({ robot }: { robot: RobotStatus }) {
    const getStatusColor = (status: string) => {
        switch (status) {
            case 'online': return 'bg-emerald-500 text-emerald-500';
            case 'charging': return 'bg-blue-500 text-blue-500';
            case 'error': return 'bg-red-500 text-red-500';
            case 'offline': return 'bg-slate-500 text-slate-500';
            default: return 'bg-slate-500';
        }
    };

    return (
        <Card className="border-slate-800 bg-slate-950/50 backdrop-blur-sm transition-all hover:bg-slate-900/50">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium text-slate-200">
                    {robot.name}
                </CardTitle>
                <Badge variant="outline" className={`border-opacity-20 bg-opacity-10 capitalize ${getStatusColor(robot.status)} border-current bg-current`}>
                    {robot.status}
                </Badge>
            </CardHeader>
            <CardContent>
                <div className="grid gap-4 py-4">
                    <div className="flex items-center gap-4">
                        <div className="grid gap-1">
                            <p className="text-sm font-medium leading-none text-slate-400">Battery</p>
                            <div className="flex items-center gap-2">
                                <Battery className="h-4 w-4 text-slate-500" />
                                <span className="text-sm font-bold text-slate-200">{robot.battery}%</span>
                            </div>
                        </div>
                        <div className="grid gap-1">
                            <p className="text-sm font-medium leading-none text-slate-400">Signal</p>
                            <div className="flex items-center gap-2">
                                <Wifi className="h-4 w-4 text-slate-500" />
                                <span className="text-sm font-bold text-slate-200">{robot.wifi}%</span>
                            </div>
                        </div>
                        <div className="grid gap-1">
                            <p className="text-sm font-medium leading-none text-slate-400">Temp</p>
                            <div className="flex items-center gap-2">
                                <Activity className="h-4 w-4 text-slate-500" />
                                <span className="text-sm font-bold text-slate-200">{robot.temperature}°C</span>
                            </div>
                        </div>
                    </div>
                    <div className="space-y-2">
                        <div className="flex items-center justify-between text-xs text-slate-400">
                            <span>Current Task</span>
                            <span className="text-slate-200">{robot.task}</span>
                        </div>
                        <Progress value={robot.battery} className="h-1 bg-slate-800" indicatorClassName={robot.battery < 20 ? "bg-red-500" : "bg-emerald-500"} />
                    </div>
                </div>
            </CardContent>
        </Card>
    )
}


function TeleopPanel() {
    return (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-7">
            {/* Main Video Feed */}
            <Card className="col-span-4 border-slate-800 bg-slate-950/50">
                <CardContent className="p-0 relative aspect-video bg-black/50 rounded-lg overflow-hidden flex items-center justify-center">
                    <div className="absolute inset-0 flex flex-col items-center justify-center text-slate-500">
                        <Video className="h-12 w-12 mb-4 opacity-50" />
                        <p>No video feed signal</p>
                    </div>
                    <div className="absolute top-2 left-2 px-2 py-1 bg-black/60 rounded text-xs text-red-500 flex items-center gap-2">
                        <div className="w-2 h-2 rounded-full bg-red-500 animate-pulse"></div>
                        LIVE
                    </div>
                </CardContent>
            </Card>

            {/* Controls */}
            <Card className="col-span-3 border-slate-800 bg-slate-950/50">
                <CardHeader>
                    <CardTitle className="text-sm font-medium text-slate-200 flex items-center gap-2">
                        <Zap className="h-4 w-4 text-yellow-500" />
                        Active Control
                    </CardTitle>
                </CardHeader>
                <CardContent className="space-y-6">
                    <div className="grid grid-cols-2 gap-4">
                        <Button variant="outline" className="h-24 w-full flex-col gap-2 border-slate-800 bg-slate-900/50 hover:bg-slate-800 hover:text-white">
                            <Play className="h-6 w-6 text-emerald-500" />
                            Start Sequence
                        </Button>
                        <Button variant="outline" className="h-24 w-full flex-col gap-2 border-slate-800 bg-slate-900/50 hover:bg-slate-800 hover:text-white">
                            <Square className="h-6 w-6 text-red-500" />
                            E-Stop
                        </Button>
                    </div>
                    <div className="space-y-2">
                        <label className="text-xs font-medium text-slate-400">Gait Mode</label>
                        <div className="grid grid-cols-3 gap-2">
                            <Button size="sm" variant="secondary" className="bg-slate-800 text-slate-300">Walk</Button>
                            <Button size="sm" variant="outline" className="border-slate-800 text-slate-400">Trot</Button>
                            <Button size="sm" variant="outline" className="border-slate-800 text-slate-400">Run</Button>
                        </div>
                    </div>
                </CardContent>
            </Card>
        </div>
    )
}
