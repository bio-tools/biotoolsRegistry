export interface ToolLite {
    id: string;
    name: string;
    version: string[];
    additionDate: string;
    lastUpdate: string;
    editPermission: {
        type: string;
        authors: string[];
    }
}

export interface User { 
    username: string;
    email: string;
    resources: ToolLite[];
    is_superuser: boolean;
    requests_count: number;
}
