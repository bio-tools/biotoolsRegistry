export interface Domain {
    domain: string;
    title: string;
    sub_title: string;
    description: string;
    is_private: boolean;
    tag: string[];
    collection: string[];
    resources: {
        biotoolsID: string;
        name: string;
    }[];
}