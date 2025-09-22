import { Routes } from '@angular/router';
import { About } from './pages/about/about';
import { Home } from './pages/home/home';
import { Search } from './pages/search/search';
import { Domains } from './pages/domains/domains';
import { Communities } from './pages/communities/communities';

export const routes: Routes = [
    { path: '', component: Home },
    { path: 'home', redirectTo: '', pathMatch: 'full' },
    { path: 'about', component: About },
    { path: 't', component: Search },
    { path: 'domains', component: Domains },
    { path: 'communities', component: Communities }
];
