import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { ScrollArea } from '@/components/ui/scroll-area';
import { BookOpen, Shield, Terminal, Wrench } from 'lucide-react';

const SAFETY_ENV = [
    { name: 'PYWINAUTO_MCP_KILL_SWITCH', note: 'Set to 1 to block mutating mouse/keyboard actions.' },
    { name: 'PYWINAUTO_MCP_MAX_ACTIONS_PER_MINUTE', note: 'Rolling 60s cap for mutating actions (default 120).' },
    { name: 'PYWINAUTO_MCP_DRY_RUN', note: 'Set to 1 to count actions without sending input to the OS.' },
    { name: 'PYWINAUTO_MCP_ENABLE_FACE', note: 'Set to 1 to register automation_face (requires face extra / deps).' },
];

const TOOLS = [
    { name: 'automation_windows', note: 'Find, focus, resize, close windows.' },
    { name: 'automation_elements', note: 'Click, type, read UI elements.' },
    { name: 'automation_mouse', note: 'Pointer moves and clicks (HITL may apply).' },
    { name: 'automation_keyboard', note: 'Keys and shortcuts (HITL may apply).' },
    { name: 'automation_visual', note: 'Screenshots, OCR, template match.' },
    {
        name: 'automation_face',
        note: 'Optional. Local UVC / built-in camera via OpenCV index (see docs/SAFETY.md §5). Tapo/IP cameras not supported for capture.',
    },
    { name: 'automation_system', note: 'status, help, wait, clipboard, processes, start_app, etc.' },
    { name: 'get_desktop_state', note: 'Structured UI tree / discovery.' },
    { name: 'approve_automation', note: 'Extends HITL approval window (app module).' },
    { name: 'automation_safety', note: 'Rate counters, kill switch / dry-run visibility.' },
];

export function Help() {
    return (
        <div className="p-6 space-y-6 max-w-4xl">
            <div>
                <h1 className="text-2xl font-semibold tracking-tight text-white">Help</h1>
                <p className="text-slate-400 mt-1">
                    Local reference for this MCP server. Authoritative docs live in the repository under{' '}
                    <code className="text-slate-300">docs/</code>.
                </p>
            </div>

            <Card className="border-slate-800 bg-slate-950/50">
                <CardHeader>
                    <CardTitle className="text-white flex items-center gap-2 text-lg">
                        <Shield className="h-5 w-5 text-amber-500" />
                        Safety and isolation
                    </CardTitle>
                </CardHeader>
                <CardContent className="text-slate-300 text-sm space-y-3">
                    <p>
                        This server drives the <strong className="text-slate-200">real Windows session</strong>. It is not
                        browser-sandboxed. Read <code className="text-slate-300">docs/SAFETY.md</code> before enabling in
                        an IDE.
                    </p>
                    <ul className="list-disc pl-5 space-y-1">
                        <li>
                            Use <strong className="text-slate-200">virtualization-mcp</strong> (separate project) if you
                            need Windows Sandbox / disposable VMs.
                        </li>
                        <li>
                            Mouse/keyboard mutations may require <strong className="text-slate-200">approve_automation</strong>{' '}
                            (HITL) depending on configuration.
                        </li>
                        <li>
                            For long desktop runs, see <code className="text-slate-300">docs/OPERATOR_PROTOCOL.md</code>{' '}
                            (keep the target app focused; avoid stealing focus from automation).
                        </li>
                    </ul>
                </CardContent>
            </Card>

            <Card className="border-slate-800 bg-slate-950/50">
                <CardHeader>
                    <CardTitle className="text-white flex items-center gap-2 text-lg">
                        <Terminal className="h-5 w-5 text-slate-400" />
                        Environment variables
                    </CardTitle>
                </CardHeader>
                <CardContent>
                    <ScrollArea className="h-[220px] pr-4">
                        <table className="w-full text-sm text-left">
                            <thead>
                                <tr className="border-b border-slate-800 text-slate-500">
                                    <th className="py-2 pr-4 font-medium">Variable</th>
                                    <th className="py-2 font-medium">Purpose</th>
                                </tr>
                            </thead>
                            <tbody className="text-slate-300">
                                {SAFETY_ENV.map((row) => (
                                    <tr key={row.name} className="border-b border-slate-800/60">
                                        <td className="py-2 pr-4 font-mono text-xs text-slate-200">{row.name}</td>
                                        <td className="py-2">{row.note}</td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </ScrollArea>
                </CardContent>
            </Card>

            <Card className="border-slate-800 bg-slate-950/50">
                <CardHeader>
                    <CardTitle className="text-white flex items-center gap-2 text-lg">
                        <Wrench className="h-5 w-5 text-slate-400" />
                        MCP tools (overview)
                    </CardTitle>
                </CardHeader>
                <CardContent>
                    <ScrollArea className="h-[320px] pr-4">
                        <ul className="space-y-2 text-sm text-slate-300">
                            {TOOLS.map((t) => (
                                <li key={t.name}>
                                    <code className="text-emerald-400/90">{t.name}</code>
                                    <span className="text-slate-500"> — </span>
                                    {t.note}
                                </li>
                            ))}
                        </ul>
                    </ScrollArea>
                </CardContent>
            </Card>

            <Card className="border-slate-800 bg-slate-950/50">
                <CardHeader>
                    <CardTitle className="text-white flex items-center gap-2 text-lg">
                        <BookOpen className="h-5 w-5 text-slate-400" />
                        MCP help from the client
                    </CardTitle>
                </CardHeader>
                <CardContent className="text-slate-300 text-sm space-y-2">
                    <p>
                        Call <code className="text-slate-200">automation_system(&quot;help&quot;)</code> for a JSON
                        overview (version, tool list, safety pointers). Same information is maintained in the server
                        code so agents can retrieve it without this UI.
                    </p>
                </CardContent>
            </Card>
        </div>
    );
}
