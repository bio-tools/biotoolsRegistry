import { Routes } from '@angular/router';
import { Home } from './pages/home/home';
import { Search } from './pages/search/search';
import { Domains } from './pages/domains/domains.component';
import { Communities } from './pages/communities/communities.component';

export const routes: Routes = [
  { path: '', component: Home },
  { path: 'home', redirectTo: '', pathMatch: 'full' },
  { path: 'search', component: Search },
  { path: 'domains', component: Domains },
  { path: 'communities', component: Communities },
  { path: '**', redirectTo: '' } // Wildcard route for 404
];
