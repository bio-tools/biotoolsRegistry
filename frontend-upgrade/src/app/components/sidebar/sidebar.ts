import { Component } from '@angular/core';
import { ACCESSIBILITY, COST, ELIXIR_COMMUNITIES, ELIXIR_NODES, ELIXIR_PLATFORMS, LICENSES, MATURITY, OPERATING_SYSTEMS, PROGRAMMING_LANGUAGES, ProgrammingLanguage, TOOL_TYPES } from '../../model/resource.model';
import { MatCheckbox } from '@angular/material/checkbox';
import { MatCard, MatCardContent, MatCardHeader, MatCardTitle } from '@angular/material/card';
import { MatExpansionModule } from '@angular/material/expansion';

@Component({
  selector: 'app-sidebar',
  imports: [
    MatCheckbox,
    MatCard,
    MatCardHeader, 
    MatCardContent,
    MatCardTitle,
    MatExpansionModule
  ],
  templateUrl: './sidebar.html',
  styleUrl: './sidebar.scss'
})
export class Sidebar {

  programmingLanguages = PROGRAMMING_LANGUAGES;
  toolTypes = TOOL_TYPES;
  licenses = LICENSES;
  cost = COST;
  operatingSystems = OPERATING_SYSTEMS;
  accessibility = ACCESSIBILITY;
  maturity = MATURITY;
  elixirPatforms = ELIXIR_PLATFORMS;
  elixirCommunities = ELIXIR_COMMUNITIES;
  elixirNodes = ELIXIR_NODES;


  // documentation true / false
  // publication true / false

  // edam topics, operation, input, output...


  selectedLangs = new Set<ProgrammingLanguage>();

  toggleLang(lang: ProgrammingLanguage, checked: boolean) {
    checked ? this.selectedLangs.add(lang) : this.selectedLangs.delete(lang);
    // Debug: log current selection to console
    // Convert set to array for readable log
    console.log('[Sidebar] Selected languages:', Array.from(this.selectedLangs));
  }
}
