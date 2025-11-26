import { Injectable, signal } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { OperatingSystem, ProgrammingLanguage, ToolType } from '../model/resource.model';

export interface FilterState {
  hasPublication?: boolean | null;
  hasDocumentation?: boolean | null;
  isFreeOfCharge?: boolean;
  isOpenAccess?: boolean;
  languages?: string[];
  licenses?: string[];
  maturity?: string[];
  operatingSystems?: string[];
  toolTypes?: string[];
}

@Injectable({
  providedIn: 'root'
})
export class FilterService {
  
  private filters = signal<FilterState>({});

  constructor(private router: Router, private route: ActivatedRoute) {}

  getFilters() {
    return this.filters;
  }

  updateFilters(newFilters: Partial<FilterState>) {
    this.filters.update(current => ({ ...current, ...newFilters }));
    this.applyFiltersToUrl();
  }

  clearFilters() {
    this.filters.set({});
    this.applyFiltersToUrl();
  }

  private applyFiltersToUrl() {
    const current = this.filters();
      console.log('Current filters:', current);

    const queryParams = {
      language: current.languages?.length ? current.languages.join(',') : null,
      license: current.licenses?.length ? current.licenses.join(',') : null,
      operatingSystem: current.operatingSystems?.length ? current.operatingSystems.join(',') : null,
      toolType: current.toolTypes?.length ? current.toolTypes.join(',') : null,
      cost: current.isFreeOfCharge ? 'Free of charge' : null,
      accessibility: current.isOpenAccess ? 'Open access' : null,
      hasPublication: current.hasPublication ? 'true' : null,
      hasDocumentation: current.hasDocumentation ? 'true' : null
    };
    
    this.router.navigate([], {
      relativeTo: this.route,
      queryParams,
      queryParamsHandling: ''
    });
  }

  initFromParams(params: any) {
    const filters: FilterState = {};
    
    if (params.language) filters.languages = params.language.split(',');
    if (params.license) filters.licenses = params.license.split(',');
    if (params.operatingSystem) filters.operatingSystems = params.operatingSystem.split(',');
    if (params.toolType) filters.toolTypes = params.toolType.split(',');
    
        // Boolean filters
    if (params.cost === 'Free of charge') filters.isFreeOfCharge = true;
    if (params.accessibility === 'Open access') filters.isOpenAccess = true;
    //if (params.hasPublication === 'true') filters.hasPublication = true;
    //if (params.hasDocumentation === 'true') filters.hasDocumentation = true;
   
    this.filters.set(filters);
  }

}
