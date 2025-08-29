export interface Domain {
  name: string;
  description: string;
  slug: string;
  toolCount: number;
  subcategories?: string[];
  color?: string;
  icon?: string;
}

export interface Community {
  name: string;
  description: string;
  slug: string;
  memberCount: number;
  toolCount: number;
  website?: string;
  contact?: string;
  logo?: string;
  tags?: string[];
  established?: string;
}
